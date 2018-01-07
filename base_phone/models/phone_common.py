# -*- coding: utf-8 -*-
# © 2010-2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api
from .. import fields as phone_fields
import logging
_logger = logging.getLogger(__name__)

try:
    import phonenumbers
except ImportError:
    _logger.debug('Cannot `import phonenumbers`.')


class PhoneCommon(models.AbstractModel):
    _name = 'phone.common'

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
        For example : ('res.partner', 42, u'Alexis de Lattre (Akretion)')
        '''
        _logger.debug(
            "Call get_name_from_phone_number with number = %s"
            % presented_number)
        if not isinstance(presented_number, str):
            _logger.warning(
                "Number '%s' should be a 'str' or 'unicode' but it is a '%s'"
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
            pg_search_number = str('%' + end_number_to_match)
            _logger.debug(
                "Will search phone and mobile numbers in %s ending with '%s'",
                obj._name, end_number_to_match)
            domain = []
            for field in obj_dict['fields']:
                domain.append((field, '=like', pg_search_number))
            if len(domain) > 1:
                domain = ['|'] * (len(domain) - 1) + domain
            _logger.debug('searching on %s with domain=%s', obj._name, domain)
            res_obj = obj.search(domain)
            if len(res_obj) > 1:
                _logger.warning(
                    "There are several %s (IDS = %s) with a phone number "
                    "ending with '%s'. Taking the first one.",
                    obj._name, res_obj.ids, end_number_to_match)
                res_obj = res_obj[0]
            if res_obj:
                name = res_obj.name_get()[0][1]
                res = (obj._name, res_obj.id, name)
                _logger.debug(
                    "Answer get_record_from_phone_number: (%s, %d, %s)",
                    res[0], res[1], res[2])
                return res
            else:
                _logger.debug(
                    "No match on %s for end of phone number '%s'",
                    obj._name, end_number_to_match)
        return False

    @api.model
    def _get_phone_models(self):
        phoneobj = []
        for model_name in list(self.env.registry.keys()):
            senv = False
            try:
                senv = self.with_context(callerid=True).env[model_name]
            except:
                continue
            if (
                    hasattr(senv, '_phone_name_sequence') and
                    isinstance(senv._phone_name_sequence, int)):
                phoneobj.append((senv, senv._phone_name_sequence))

        phoneobj_sorted = sorted(phoneobj, key=lambda element: element[1])

        res = []
        for (obj, prio) in phoneobj_sorted:
            entry = {'object': obj, 'fields': []}
            for field in obj._fields:
                if isinstance(obj._fields[field], phone_fields.Phone):
                    entry['fields'].append(field)
            res.append(entry)
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
        try:
          parsed_num = phonenumbers.parse(erp_number, None)
        except:
          parsed_num = phonenumbers.parse(erp_number, region='US')
        country_code = self.env.user.company_id.country_id.code
        assert(country_code), 'Missing country on company'
        _logger.debug('Country code = %s' % country_code)
        to_dial_number = phonenumbers.format_out_of_country_calling_number(
            parsed_num, country_code.upper())
        to_dial_number = str(to_dial_number).translate(str.maketrans('','', ' -.()/'))
        _logger.debug('Number to be sent to phone system: %s' % to_dial_number)
        return to_dial_number
