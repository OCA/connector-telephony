# Copyright 2010-2018 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api
import logging
_logger = logging.getLogger(__name__)

try:
    import phonenumbers
except ImportError:
    _logger.debug('Cannot `import phonenumbers`.')


class PhoneCommon(models.AbstractModel):
    _name = 'phone.common'
    _description = 'Common methods for phone features'

    @api.model
    def get_name_from_phone_number(self, presented_number):
        '''Function to get name from phone number. Usefull for use from IPBX
        to add CallerID name to incoming calls.'''
        res = self.get_record_from_phone_number(presented_number)
        if res:
            return res[2]
        else:
            return False

    @api.model
    def get_record_from_phone_number(self, presented_number):
        '''If it finds something, it returns (object name, ID, record name)
        For example : ('res.partner', 42, 'Alexis de Lattre (Akretion)')
        '''
        _logger.debug(
            "Call get_name_from_phone_number with number = %s"
            % presented_number)
        if not isinstance(presented_number, str):
            _logger.warning(
                "Number '%s' should be a 'str' but it is a '%s'"
                % (presented_number, type(presented_number)))
            return False
        if not presented_number.isdigit():
            _logger.warning(
                "Number '%s' should only contain digits." % presented_number)

        nr_digits_to_match_from_end = \
            self.env.user.company_id.number_of_digits_to_match_from_end
        if len(presented_number) >= nr_digits_to_match_from_end:
            end_number_to_match = presented_number[
                -nr_digits_to_match_from_end:len(presented_number)]
        else:
            end_number_to_match = presented_number

        sorted_phonemodels = self._get_phone_models()
        for obj_dict in sorted_phonemodels:
            obj = obj_dict['object']
            pg_search_number = '%' + end_number_to_match
            _logger.debug(
                "Will search phone and mobile numbers in %s ending with '%s'",
                obj._name, end_number_to_match)
            sql = "SELECT id FROM %s WHERE " % obj._table
            sql_where = []
            sql_args = []
            for field in obj_dict['fields']:
                sql_where.append("replace(%s, ' ', '') ilike %%s" % field)
                sql_args.append(pg_search_number)
            sql = sql + ' or '.join(sql_where)
            _logger.debug("get_record_from_phone_number sql=%s", sql)
            self._cr.execute(sql, tuple(sql_args))
            res_sql = self._cr.fetchall()
            if len(res_sql) > 1:
                res_ids = [x[0] for x in res_sql]
                _logger.warning(
                    u"There are several %s (IDS = %s) with a phone number "
                    "ending with '%s'. Taking the first one.",
                    obj._name, res_ids, end_number_to_match)
            if res_sql:
                obj_id = res_sql[0][0]
                res_obj = obj.browse(obj_id)
                name = res_obj.display_name
                res = (obj._name, res_obj.id, name)
                _logger.debug(
                    u"Answer get_record_from_phone_number: (%s, %d, %s)",
                    res[0], res[1], res[2])
                return res
            else:
                _logger.debug(
                    u"No match on %s for end of phone number '%s'",
                    obj._name, end_number_to_match)
        return False

    @api.model
    def _get_phone_models(self):
        phoneobj = []
        for model_name in self.env.registry.keys():
            senv = False
            try:
                senv = self.with_context(callerid=True).env[model_name]
            except Exception:
                continue
            if (
                    hasattr(senv, '_phone_name_sequence') and
                    isinstance(senv._phone_name_sequence, int) and
                    hasattr(senv, '_phone_name_fields') and
                    isinstance(senv._phone_name_fields, list)):
                cdict = {
                    'object': senv,
                    'fields': senv._phone_name_fields,
                    }
                phoneobj.append((senv._phone_name_sequence, cdict))

        phoneobj_sorted = sorted(phoneobj, key=lambda element: element[0])
        res = []
        for l in phoneobj_sorted:
            res.append(l[1])
        # [{'fields': ['fax', 'phone', 'mobile'], 'object': res.partner()},
        #  {'fields': ['fax', 'phone', 'mobile'], 'object': crm.lead()}]
        return res

    @api.model
    def click2dial(self, erp_number):
        '''This function is designed to be overridden in IPBX-specific
        modules, such as asterisk_click2dial or ovh_telephony_connector'''
        return {'dialed_number': erp_number}

    @api.model
    def convert_to_dial_number(self, erp_number):
        '''
        This function is dedicated to the transformation of the number
        available in Odoo to the number that can be dialed.
        You may have to inherit this function in another module specific
        for your company if you are not happy with the way I reformat
        the numbers.
        '''
        assert(erp_number), 'Missing phone number'
        _logger.debug('Number before reformat = %s' % erp_number)
        # erp_number are supposed to be in International format, so no need to
        # give a country code here
        parsed_num = phonenumbers.parse(erp_number, None)
        country_code = self.env.user.company_id.country_id.code
        assert(country_code), 'Missing country on company'
        _logger.debug('Country code = %s' % country_code)
        to_dial_number = phonenumbers.format_out_of_country_calling_number(
            parsed_num, country_code.upper())
        to_dial_number = to_dial_number.translate(
            to_dial_number.maketrans('', '', ' -.()/'))
        _logger.debug('Number to be sent to phone system: %s' % to_dial_number)
        return to_dial_number
