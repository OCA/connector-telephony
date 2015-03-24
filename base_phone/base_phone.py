# -*- encoding: utf-8 -*-
##############################################################################
#
#    Base Phone module for Odoo/OpenERP
#    Copyright (C) 2010-2014 Alexis de Lattre <alexis@via.ecp.fr>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api, _
from openerp.tools.safe_eval import safe_eval
from openerp.exceptions import Warning
import logging
# Lib for phone number reformating -> pip install phonenumbers
import phonenumbers

_logger = logging.getLogger(__name__)


class PhoneCommon(models.AbstractModel):
    _name = 'phone.common'

    def _generic_reformat_phonenumbers(
            self, cr, uid, ids, vals, context=None):
        """Reformat phone numbers in E.164 format i.e. +33141981242"""
        assert isinstance(self._country_field, (str, unicode, type(None))),\
            'Wrong self._country_field'
        assert isinstance(self._partner_field, (str, unicode, type(None))),\
            'Wrong self._partner_field'
        assert isinstance(self._phone_fields, list),\
            'self._phone_fields must be a list'
        if context is None:
            context = {}
        if ids and isinstance(ids, (int, long)):
            ids = [ids]
        if any([vals.get(field) for field in self._phone_fields]):
            user = self.pool['res.users'].browse(cr, uid, uid, context=context)
            # country_id on res.company is a fields.function that looks at
            # company_id.partner_id.addres(default).country_id
            countrycode = None
            if self._country_field:
                if vals.get(self._country_field):
                    country = self.pool['res.country'].browse(
                        cr, uid, vals[self._country_field], context=context)
                    countrycode = country.code
                elif ids:
                    rec = self.browse(cr, uid, ids[0], context=context)
                    country = safe_eval(
                        'rec.' + self._country_field, {'rec': rec})
                    countrycode = country and country.code or None
            elif self._partner_field:
                if vals.get(self._partner_field):
                    partner = self.pool['res.partner'].browse(
                        cr, uid, vals[self._partner_field], context=context)
                    countrycode = partner.country_id and\
                        partner.country_id.code or None
                elif ids:
                    rec = self.browse(cr, uid, ids[0], context=context)
                    partner = safe_eval(
                        'rec.' + self._partner_field, {'rec': rec})
                    if partner:
                        countrycode = partner.country_id and\
                            partner.country_id.code or None
            if not countrycode:
                if user.company_id.country_id:
                    countrycode = user.company_id.country_id.code
                else:
                    _logger.error(
                        _("You should set a country on the company '%s' "
                            "to allow the reformat of phone numbers")
                        % user.company_id.name)
                    countrycode = None
                # with country code = None, phonenumbers.parse() will work
                # with phonenumbers formatted in E164, but will fail with
                # phone numbers in national format
            for field in self._phone_fields:
                if vals.get(field):
                    init_value = vals.get(field)
                    try:
                        res_parse = phonenumbers.parse(
                            vals.get(field), countrycode)
                        vals[field] = phonenumbers.format_number(
                            res_parse, phonenumbers.PhoneNumberFormat.E164)
                        if init_value != vals[field]:
                            _logger.info(
                                "%s initial value: '%s' updated value: '%s'"
                                % (field, init_value, vals[field]))
                    except Exception, e:
                        # I do BOTH logger and raise, because:
                        # raise is usefull when the record is created/written
                        #    by a user via the Web interface
                        # logger is usefull when the record is created/written
                        #    via the webservices
                        _logger.error(
                            "Cannot reformat the phone number '%s' to "
                            "international format with region=%s"
                            % (vals.get(field), countrycode))
                        if context.get('raise_if_phone_parse_fails'):
                            raise Warning(
                                _("Cannot reformat the phone number '%s' to "
                                    "international format. Error message: %s")
                                % (vals.get(field), e))
        return vals

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
            u"Call get_name_from_phone_number with number = %s"
            % presented_number)
        if not isinstance(presented_number, (str, unicode)):
            _logger.warning(
                u"Number '%s' should be a 'str' or 'unicode' but it is a '%s'"
                % (presented_number, type(presented_number)))
            return False
        if not presented_number.isdigit():
            _logger.warning(
                u"Number '%s' should only contain digits." % presented_number)

        nr_digits_to_match_from_end = \
            self.env.user.company_id.number_of_digits_to_match_from_end
        if len(presented_number) >= nr_digits_to_match_from_end:
            end_number_to_match = presented_number[
                -nr_digits_to_match_from_end:len(presented_number)]
        else:
            end_number_to_match = presented_number

        phoneobjects = self._get_phone_fields()
        phonefieldslist = []  # [('res.parter', 10), ('crm.lead', 20)]
        for objname in phoneobjects:
            if (
                    '_phone_name_sequence' in dir(self.env[objname]) and
                    self.env[objname]._phone_name_sequence):
                phonefieldslist.append(
                    (objname, self.env[objname]._phone_name_sequence))
        phonefieldslist_sorted = sorted(
            phonefieldslist,
            key=lambda element: element[1])
        _logger.debug('phonefieldslist_sorted=%s' % phonefieldslist_sorted)
        for (objname, prio) in phonefieldslist_sorted:
            obj = self.with_context(callerid=True).env[objname]
            pg_search_number = str('%' + end_number_to_match)
            _logger.debug(
                "Will search phone and mobile numbers in %s ending with '%s'"
                % (objname, end_number_to_match))
            domain = []
            for phonefield in obj._phone_fields:
                domain.append((phonefield, '=like', pg_search_number))
            if len(obj._phone_fields) > 1:
                domain = ['|'] * (len(obj._phone_fields) - 1) + domain
            res_obj = obj.search(domain)
            if len(res_obj) > 1:
                _logger.warning(
                    u"There are several %s (IDS = %s) with a phone number "
                    "ending with '%s'. Taking the first one."
                    % (objname, res_obj.ids, end_number_to_match))
                res_obj = res_obj[0]
            if res_obj:
                name = res_obj.name_get()[0][1]
                res = (objname, res_obj.id, name)
                _logger.debug(
                    u"Answer get_record_from_phone_number: (%s, %d, %s)"
                    % (res[0], res[1], res[2]))
                return res
            else:
                _logger.debug(
                    u"No match on %s for end of phone number '%s'"
                    % (objname, end_number_to_match))
        return False

    @api.model
    def _get_phone_fields(self):
        '''Returns a dict with key = object name
        and value = list of phone fields'''
        models = self.env['ir.model'].search([('osv_memory', '=', False)])
        res = []
        for model in models:
            senv = False
            try:
                senv = self.env[model.model]
            except:
                continue
            if (
                    '_phone_fields' in dir(senv) and
                    isinstance(senv._phone_fields, list)):
                res.append(model.model)
        return res

    def click2dial(self, cr, uid, erp_number, context=None):
        '''This function is designed to be overridden in IPBX-specific
        modules, such as asterisk_click2dial'''
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
        # erp_number are supposed to be in E.164 format, so no need to
        # give a country code here
        parsed_num = phonenumbers.parse(erp_number, None)
        country_code = self.env.user.company_id.country_id.code
        assert(country_code), 'Missing country on company'
        _logger.debug('Country code = %s' % country_code)
        to_dial_number = phonenumbers.format_out_of_country_calling_number(
            parsed_num, country_code.upper())
        to_dial_number = str(to_dial_number).translate(None, ' -.()/')
        _logger.debug('Number to be sent to Asterisk = %s' % to_dial_number)
        return to_dial_number


class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = ['res.partner', 'phone.common']
    _phone_fields = ['phone', 'mobile', 'fax']
    _phone_name_sequence = 10
    _country_field = 'country_id'
    _partner_field = None

    def create(self, cr, uid, vals, context=None):
        vals_reformated = self._generic_reformat_phonenumbers(
            cr, uid, None, vals, context=context)
        return super(ResPartner, self).create(
            cr, uid, vals_reformated, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        vals_reformated = self._generic_reformat_phonenumbers(
            cr, uid, ids, vals, context=context)
        return super(ResPartner, self).write(
            cr, uid, ids, vals_reformated, context=context)

    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if context.get('callerid'):
            res = []
            if isinstance(ids, (int, long)):
                ids = [ids]
            for partner in self.browse(cr, uid, ids, context=context):
                if partner.parent_id and partner.parent_id.is_company:
                    name = u'%s (%s)' % (partner.name, partner.parent_id.name)
                else:
                    name = partner.name
                res.append((partner.id, name))
            return res
        else:
            return super(ResPartner, self).name_get(
                cr, uid, ids, context=context)


class ResCompany(models.Model):
    _inherit = 'res.company'

    number_of_digits_to_match_from_end = fields.Integer(
        string='Number of Digits To Match From End',
        default=8,
        help="In several situations, OpenERP will have to find a "
        "Partner/Lead/Employee/... from a phone number presented by the "
        "calling party. As the phone numbers presented by your phone "
        "operator may not always be displayed in a standard format, "
        "the best method to find the related Partner/Lead/Employee/... "
        "in OpenERP is to try to match the end of the phone number in "
        "OpenERP with the N last digits of the phone number presented "
        "by the calling party. N is the value you should enter in this "
        "field.")

    _sql_constraints = [(
        'number_of_digits_to_match_from_end_positive',
        'CHECK (number_of_digits_to_match_from_end > 0)',
        "The value of the field 'Number of Digits To Match From End' must "
        "be positive."),
        ]
