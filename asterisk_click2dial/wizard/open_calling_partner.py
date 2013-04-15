# -*- encoding: utf-8 -*-
##############################################################################
#
#    Asterisk Click2dial module for OpenERP
#    Copyright (C) 2010-2013 Alexis de Lattre <alexis@via.ecp.fr>
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

from osv import osv, fields
import netsvc
# Lib to translate error messages
from tools.translate import _

logger = netsvc.Logger()


class wizard_open_calling_partner(osv.osv_memory):
    _name = "wizard.open.calling.partner"
    _description = "Open calling partner"

    _columns = {
        # I can't set any field to readonly, because otherwize it would call
        # default_get (and thus connect to Asterisk) a second time when the user
        # clicks on one of the buttons
        'calling_number': fields.char('Calling number', size=30, help="Phone number of calling party that has been obtained from Asterisk."),
        'partner_address_id': fields.many2one('res.partner.address', 'Contact name', help="Partner contact related to the calling number. If there is none and you want to update an existing partner"),
        'partner_id': fields.many2one('res.partner', 'Partner', help="Partner related to the calling number."),
        'to_update_partner_address_id': fields.many2one('res.partner.address', 'Contact to update', help="Partner contact on which the phone or mobile number will be written"),
        'current_phone': fields.related('to_update_partner_address_id', 'phone', type='char', relation='res.partner.address', string='Current phone'),
        'current_mobile': fields.related('to_update_partner_address_id', 'mobile', type='char', relation='res.partner.address', string='Current mobile'),
            }


    def default_get(self, cr, uid, fields, context=None):
        '''Thanks to the default_get method, we are able to query Asterisk and
        get the corresponding partner when we launch the wizard'''
        res = {}
        #calling_number = self.pool.get('asterisk.server')._get_calling_number(cr, uid, context=context)
        #To test the code without Asterisk server
        calling_number = "0141981242"
        if calling_number:
            res['calling_number'] = calling_number
            partner = self.pool.get('res.partner.address').get_partner_from_phone_number(cr, uid, calling_number, context=context)
            if partner:
                res['partner_address_id'] = partner[0]
                res['partner_id'] = partner[1]
            else:
                res['partner_id'] = False
                res['partner_address_id'] = False
            res['to_update_partner_address_id'] = False
        else:
            logger.notifyChannel('click2dial', netsvc.LOG_DEBUG, "Could not get the calling number from Asterisk.")
            raise osv.except_osv(_('Error :'), _("Could not get the calling number from Asterisk. Are you currently on the phone ? If yes, check your setup and look at the OpenERP debug logs."))

        return res


    def open_filtered_object(self, cr, uid, ids, oerp_object, context=None):
        '''Returns the action that opens the list view of the 'oerp_object'
        given as argument filtered on the partner'''
        # This module only depends on "base"
        # and I don't want to add a dependancy on "sale" or "account"
        # So I just check here that the model exists, to avoid a crash
        if not self.pool.get('ir.model').search(cr, uid, [('model', '=', oerp_object._name)], context=context):
            raise osv.except_osv(_('Error :'), _("The object '%s' is not found in your OpenERP database, probably because the related module is not installed." % oerp_object._description))

        partner_id = self.browse(cr, uid, ids[0], context=context).partner_id.id
        if partner_id:
            action = {
                'name': oerp_object._description,
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': oerp_object._name,
                'type': 'ir.actions.act_window',
                'nodestroy': False, # close the pop-up wizard after action
                'target': 'current',
                'domain': [('partner_id', '=', partner_id)],
                }
            return action
        else:
            return False


    def open_sale_orders(self, cr, uid, ids, context=None):
        '''Function called by the related button of the wizard'''
        return self.open_filtered_object(cr, uid, ids, self.pool.get('sale.order'), context=context)


    def open_invoices(self, cr, uid, ids, context=None):
        '''Function called by the related button of the wizard'''
        return self.open_filtered_object(cr, uid, ids, self.pool.get('account.invoice'), context=context)


    def simple_open(self, cr, uid, ids, object_name='res.partner', context=None):
        if object_name == 'res.partner':
            record_id = self.browse(cr, uid, ids[0], context=context).partner_id.id
            label = 'Partner'
        elif object_name == 'res.partner.address':
            record_id = self.browse(cr, uid, ids[0], context=context).partner_address_id.id
            label = 'Contact'
        else:
            raise osv.except_osv(_('Error :'), "This object '%s' is not supported" % object_name)
        if record_id:
            return {
                'name': label,
                'view_type': 'form',
                'view_mode': 'form,tree',
                'res_model': object_name,
                'type': 'ir.actions.act_window',
                'nodestroy': False, # close the pop-up wizard after action
                'target': 'current',
                'res_id': record_id,
                }
        else:
            return False


    def open_partner(self, cr, uid, ids, context=None):
        '''Function called by the related button of the wizard'''
        return self.simple_open(cr, uid, ids, object_name='res.partner', context=context)


    def open_partner_address(self, cr, uid, ids, context=None):
        '''Function called by the related button of the wizard'''
        return self.simple_open(cr, uid, ids, object_name='res.partner.address', context=context)


    def create_partner_address(self, cr, uid, ids, phone_type='phone', context=None):
        '''Function called by the related button of the wizard'''
        calling_number = self.read(cr, uid, ids[0], ['calling_number'], context=context)['calling_number']
        ast_server = self.pool.get('asterisk.server')._get_asterisk_server_from_user(cr, uid, context=context)
        # Convert the number to the international format
        number_to_write = self.pool.get('asterisk.server')._convert_number_to_international_format(cr, uid, calling_number, ast_server, context=context)

        context['default_' + phone_type] = number_to_write
        action = {
            'name': 'Create new contact',
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'res.partner.address',
            'type': 'ir.actions.act_window',
            'nodestroy': False,
            'target': 'current',
            'context': context,
        }
        return action


    def create_partner_address_phone(self, cr, uid, ids, context=None):
        return self.create_partner_address(cr, uid, ids, phone_type='phone', context=context)


    def create_partner_address_mobile(self, cr, uid, ids, context=None):
        return self.create_partner_address(cr, uid, ids, phone_type='mobile', context=context)


    def update_partner_address(self, cr, uid, ids, phone_type='mobile', context=None):
        cur_wizard = self.browse(cr, uid, ids[0], context=context)
        if not cur_wizard.to_update_partner_address_id:
            raise osv.except_osv(_('Error :'), _("Select the contact to update."))
        ast_server = self.pool.get('asterisk.server')._get_asterisk_server_from_user(cr, uid, context=context)
        number_to_write = self.pool.get('asterisk.server')._convert_number_to_international_format(cr, uid, cur_wizard.calling_number, ast_server, context=context)
        self.pool.get('res.partner.address').write(cr, uid, cur_wizard.to_update_partner_address_id.id, {phone_type: number_to_write}, context=context)
        action = {
            'name': 'Contact: ' + cur_wizard.to_update_partner_address_id.name,
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'res.partner.address',
            'type': 'ir.actions.act_window',
            'nodestroy': False,
            'target': 'current',
            'res_id': cur_wizard.to_update_partner_address_id.id
            }
        return action


    def update_partner_address_phone(self, cr, uid, ids, context=None):
        return self.update_partner_address(cr, uid, ids, phone_type='phone', context=context)


    def update_partner_address_mobile(self, cr, uid, ids, context=None):
        return self.update_partner_address(cr, uid, ids, phone_type='mobile', context=context)


    def onchange_to_update_partner_address(self, cr, uid, ids, to_update_partner_address_id, context=None):
        res = {}
        res['value'] = {}
        if to_update_partner_address_id:
            to_update_partner_address = self.pool.get('res.partner.address').browse(cr, uid, to_update_partner_address_id, context=context)
            res['value'].update({'current_phone': to_update_partner_address.phone,
                'current_mobile': to_update_partner_address.mobile})
        else:
            res['value'].update({'current_phone': False, 'current_mobile': False})
        return res

wizard_open_calling_partner()
