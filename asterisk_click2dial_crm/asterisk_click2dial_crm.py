# -*- encoding: utf-8 -*-
##############################################################################
#
#    Asterisk click2dial CRM module for OpenERP
#    Copyright (c) 2011 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
#    Copyright (c) 2012-2013 Akretion (http://www.akretion.com)
#    @author: Jesús Martín <jmartin@zikzakmedia.com>
#    @author: Alexis de Lattre <alexis.delattre@akretion.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

from openerp.osv import osv, fields
# Lib required to print logs
import logging
# Lib to translate error messages
from openerp.tools.translate import _
# Lib for phone number reformating -> pip install phonenumbers
import phonenumbers
# Lib py-asterisk from http://code.google.com/p/py-asterisk/
# We need a version which has this commit : http://code.google.com/p/py-asterisk/source/detail?r=8d0e1c941cce727c702582f3c9fcd49beb4eeaa4
# so a version after Nov 20th, 2012
from Asterisk import Manager

_logger = logging.getLogger(__name__)


class res_partner(osv.osv):
    _inherit = "res.partner"

    def dial(self, cr, uid, ids, phone_field='phone', context=None):
        '''
        This method open the phone call history when the phone click2dial
        button of asterisk_click2dial module is pressed
        :return the phone call history view of the partner
        '''
        if context is None:
            context = {}
        super(res_partner, self).dial(cr, uid, ids, phone_field=phone_field, context=context)
        user = self.pool['res.users'].browse(cr, uid, uid, context=context)
        context['partner_id'] = ids[0]
        action_start_wizard = {
            'name': 'Create phone call in CRM',
            'type': 'ir.actions.act_window',
            'res_model': 'wizard.create.crm.phonecall',
            'view_type': 'form',
            'view_mode': 'form',
            'nodestroy': True,
            'target': 'new',
            'context': context,
            }
        if user.context_propose_creation_crm_call:
            return action_start_wizard
        else:
            return True



class res_users(osv.osv):
    _inherit = "res.users"

    _columns = {
        # Field name starts with 'context_' to allow modification by the user
        # in his preferences, cf server-61/openerp/addons/base/res/res_users.py
        # line 377 in "def write" of "class users"
        'context_propose_creation_crm_call': fields.boolean('Propose to create a call in CRM after a click2dial'),
        }

    _defaults = {
        'context_propose_creation_crm_call': True,
        }

class crm_lead(osv.osv):
    _inherit = "crm.lead"


    def _format_phonenumber_to_e164(self, cr, uid, ids, name, arg, context=None):
        result = {}
        for lead in self.read(cr, uid, ids, ['phone', 'mobile', 'fax'], context=context):
            result[lead['id']] = {}
            for fromfield, tofield in [('phone', 'phone_e164'), ('mobile', 'mobile_e164'), ('fax', 'fax_e164')]:
                if not lead.get(fromfield):
                    res = False
                else:
                    try:
                        res = phonenumbers.format_number(phonenumbers.parse(lead.get(fromfield), None), phonenumbers.PhoneNumberFormat.E164)
                    except Exception, e:
                        _logger.error("Cannot reformat the phone number '%s' to E.164 format. Error message: %s" % (lead.get(fromfield), e))
                        _logger.error("You should fix this number and run the wizard 'Reformat all phone numbers' from the menu Settings > Configuration > Asterisk")
                    # If I raise an exception here, it won't be possible to install
                    # the module on a DB with bad phone numbers
                        #raise osv.except_osv(_('Error :'), _("Cannot reformat the phone number '%s' to E.164 format. Error message: %s" % (lead.get(fromfield), e)))
                        res = False
                result[lead['id']][tofield] = res
        #print "RESULT _format_phonenumber_to_e164", result
        return result


    _columns = {
        'phone_e164': fields.function(_format_phonenumber_to_e164, type='char', size=64, string='Phone in E.164 format', readonly=True, multi="e164", store={
            'crm.lead': (lambda self, cr, uid, ids, c={}: ids, ['phone'], 10),
            }),
        'mobile_e164': fields.function(_format_phonenumber_to_e164, type='char', size=64, string='Mobile in E.164 format', readonly=True, multi="e164", store={
            'crm.lead': (lambda self, cr, uid, ids, c={}: ids, ['mobile'], 10),
            }),
        'fax_e164': fields.function(_format_phonenumber_to_e164, type='char', size=64, string='Fax in E.164 format', readonly=True, multi="e164", store={
            'crm.lead': (lambda self, cr, uid, ids, c={}: ids, ['fax'], 10),
            }),
        }

    def _reformat_phonenumbers(self, cr, uid, vals, context=None):
        """Reformat phone numbers in international format i.e. +33141981242"""
        phonefields = ['phone', 'fax', 'mobile']
        if any([vals.get(field) for field in phonefields]):
            user = self.pool['res.users'].browse(cr, uid, uid, context=context)
            # country_id on res.company is a fields.function that looks at
            # company_id.partner_id.addres(default).country_id
            if user.company_id.country_id:
                user_countrycode = user.company_id.country_id.code
            else:
                # We need to raise an exception here because, if we pass None as second arg of phonenumbers.parse(), it will raise an exception when you try to enter a phone number in national format... so it's better to raise the exception here
                raise osv.except_osv(_('Error :'), _("You should set a country on the company '%s'" % user.company_id.name))
            #print "user_countrycode=", user_countrycode
            for field in phonefields:
                if vals.get(field):
                    try:
                        res_parse = phonenumbers.parse(vals.get(field), user_countrycode)
                    except Exception, e:
                        raise osv.except_osv(_('Error :'), _("Cannot reformat the phone number '%s' to international format. Error message: %s" % (vals.get(field), e)))
                    #print "res_parse=", res_parse
                    vals[field] = phonenumbers.format_number(res_parse, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        return vals


    def create(self, cr, uid, vals, context=None):
        vals_reformated = self._reformat_phonenumbers(cr, uid, vals, context=context)
        return super(crm_lead, self).create(cr, uid, vals_reformated, context=context)


    def write(self, cr, uid, ids, vals, context=None):
        vals_reformated = self._reformat_phonenumbers(cr, uid, vals, context=context)
        return super(crm_lead, self).write(cr, uid, ids, vals_reformated, context=context)


    def dial(self, cr, uid, ids, phone_field=['phone', 'phone_e164'], context=None):
        '''Read the number to dial and call _connect_to_asterisk the right way'''
        erp_number_read = self.read(cr, uid, ids[0], phone_field, context=context)
        erp_number_e164 = erp_number_read[phone_field[1]]
        erp_number_display = erp_number_read[phone_field[0]]
        # Check if the number to dial is not empty
        if not erp_number_display:
            raise osv.except_osv(_('Error :'), _('There is no phone number !'))
        elif erp_number_display and not erp_number_e164:
            raise osv.except_osv(_('Error :'), _("The phone number isn't stored in the standard E.164 format. Try to run the wizard 'Reformat all phone numbers' from the menu Settings > Configuration > Asterisk."))
        return self.pool['asterisk.server']._dial_with_asterisk(cr, uid, erp_number_e164, context=context)


    def action_dial_phone(self, cr, uid, ids, context=None):
        '''Function called by the button 'Dial' next to the 'phone' field
        in the lead view'''
        return self.dial(cr, uid, ids, phone_field=['phone', 'phone_e164'], context=context)


    def action_dial_mobile(self, cr, uid, ids, context=None):
        '''Function called by the button 'Dial' next to the 'mobile' field
        in the lead view'''
        return self.dial(cr, uid, ids, phone_field=['mobile', 'mobile_e164'], context=context)



