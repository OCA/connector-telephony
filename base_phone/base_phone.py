# -*- encoding: utf-8 -*-
##############################################################################
#
#    Base Phone module for OpenERP
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

from openerp.osv import orm
from openerp.tools.translate import _
import logging
# Lib for phone number reformating -> pip install phonenumbers
import phonenumbers

_logger = logging.getLogger(__name__)


class phone_common(orm.AbstractModel):
    _name = 'phone.common'

    def generic_phonenumber_to_e164(
            self, cr, uid, ids, field_from_to_seq, context=None):
        result = {}
        from_field_seq = [item[0] for item in field_from_to_seq]
        for record in self.read(cr, uid, ids, from_field_seq, context=context):
            result[record['id']] = {}
            for fromfield, tofield in field_from_to_seq:
                if not record.get(fromfield):
                    res = False
                else:
                    try:
                        res = phonenumbers.format_number(
                            phonenumbers.parse(record.get(fromfield), None),
                            phonenumbers.PhoneNumberFormat.E164)
                    except Exception, e:
                        _logger.error(
                            "Cannot reformat the phone number '%s' to E.164 "
                            "format. Error message: %s"
                            % (record.get(fromfield), e))
                        _logger.error(
                            "You should fix this number and run the wizard "
                            "'Reformat all phone numbers' from the menu "
                            "Settings > Configuration > Phones")
                    # If I raise an exception here, it won't be possible to
                    # install the module on a DB with bad phone numbers
                        res = False
                result[record['id']][tofield] = res
        return result

    def _generic_reformat_phonenumbers(
            self, cr, uid, vals,
            phonefields=['phone', 'partner_phone', 'fax', 'mobile'],
            context=None):
        """Reformat phone numbers in E.164 format i.e. +33141981242"""
        if any([vals.get(field) for field in phonefields]):
            user = self.pool['res.users'].browse(cr, uid, uid, context=context)
            # country_id on res.company is a fields.function that looks at
            # company_id.partner_id.addres(default).country_id
            if user.company_id.country_id:
                user_countrycode = user.company_id.country_id.code
            else:
                # We need to raise an exception here because, if we pass None
                # as second arg of phonenumbers.parse(), it will raise an
                # exception when you try to enter a phone number in
                # national format... so it's better to raise the exception here
                raise orm.except_orm(
                    _('Error :'),
                    _("You should set a country on the company '%s'")
                    % user.company_id.name)
            #print "user_countrycode=", user_countrycode
            for field in phonefields:
                if vals.get(field):
                    init_value = vals.get(field)
                    try:
                        res_parse = phonenumbers.parse(
                            vals.get(field), user_countrycode)
                    except Exception, e:
                        raise orm.except_orm(
                            _('Error :'),
                            _("Cannot reformat the phone number '%s' to "
                                "international format. Error message: %s")
                            % (vals.get(field), e))
                    #print "res_parse=", res_parse
                    vals[field] = phonenumbers.format_number(
                        res_parse, phonenumbers.PhoneNumberFormat.E164)
                    if init_value != vals[field]:
                        _logger.info(
                            "%s initial value: '%s' updated value: '%s'"
                            % (field, init_value, vals[field]))
        return vals


class res_partner(orm.Model):
    _name = 'res.partner'
    _inherit = ['res.partner', 'phone.common']

    def create(self, cr, uid, vals, context=None):
        vals_reformated = self._generic_reformat_phonenumbers(
            cr, uid, vals, context=context)
        return super(res_partner, self).create(
            cr, uid, vals_reformated, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        vals_reformated = self._generic_reformat_phonenumbers(
            cr, uid, vals, context=context)
        return super(res_partner, self).write(
            cr, uid, ids, vals_reformated, context=context)
