# -*- encoding: utf-8 -*-
##############################################################################
#
#    Asterisk click2dial CRM module for OpenERP
#    Copyright (c) 2011 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
#    Copyright (c) 2012 Akretion (http://www.akretion.com)
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

from osv import osv, fields
# Lib to translate error messages
from tools.translate import _


class wizard_create_crm_phonecall(osv.osv_memory):
    _name = "wizard.create.crm.phonecall"

    _columns = {
        # Stupid useless field, just to be able to use default_get()
        'name': fields.char('Workaround', size=12),
    }

    def default_get(self, cr, uid, fields, context=None):
        res = {}
        self.pool.get('res.partner.address').dial(cr, uid, context.get('active_ids'), phone_field=context.get('phone_field'), context=context)
        return res

    def button_create_outgoing_phonecall(self, cr, uid, ids, context=None):
        partner_address = self.pool.get('res.partner.address').browse(cr, uid, context.get('active_id'), context=context)
        return self._create_open_crm_phonecall(cr, uid, partner_address, crm_categ='Outbound', context=context)

    def _create_open_crm_phonecall(self, cr, uid, partner_address, crm_categ='Outbound', context=None):
        if context is None:
            context = {}

        data_obj = self.pool.get('ir.model.data')
        data_section_ids = data_obj.search(cr, uid, [
            ('model', '=', 'crm.case.section'),
            ('module', '=', 'crm_configuration'),
            ('name', '=', 'section_support_phone')
            ], context=context)
        default_section_id = False
        if data_section_ids:
            default_section_id = data_obj.read(cr, uid, data_section_ids[0], ['res_id'], context=context)['res_id']

        if crm_categ == 'Outbound':
            crm_categ_xmlid = 'categ_phone2'
        elif crm_categ == 'Inbound':
            crm_categ_xmlid = 'categ_phone1'
        else:
            raise
        data_categ_ids = data_obj.search(cr, uid, [
            ('model', '=', 'crm.case.categ'),
            ('module', '=', 'crm_configuration'),
            ('name', '=', crm_categ_xmlid)
            ], context=context)
        default_categ_id = False
        if data_categ_ids:
            default_categ_id = data_obj.read(cr, uid, data_categ_ids[0], ['res_id'], context=context)['res_id']


        context.update({
            'default_partner_id': partner_address.partner_id and partner_address.partner_id.id or False,
            'default_partner_address_id': partner_address.id,
            'default_partner_mobile': partner_address.mobile,
            'default_partner_phone': partner_address.phone,
            'default_section_id': default_section_id,
            'default_categ_id': default_categ_id,
            'default_user_id': uid,
        })

        data_view_ids = data_obj.search(cr, uid, [
            ('model', '=', 'ir.ui.view'),
            ('name', '=', 'crm_case_phone_form_view'),
            ('module', '=', 'crm_configuration')
            ], context=context)
        view_id = False
        if data_view_ids:
            view_id = data_obj.read(cr, uid, data_view_ids[0], ['res_id'], context=context)['res_id']

        return {
            'name': partner_address.name,
            'res_model': 'crm.case',
            'view_type': 'form',
            'view_mode': 'form,tree',
            'view_id': [view_id],
            'type': 'ir.actions.act_window',
            'nodestroy': False, # close the pop-up wizard after action
            'target': 'current',
            'context': context,
        }

wizard_create_crm_phonecall()


# CODE MOVED to asterisk_click2dial, because we can't inherit a wizard in OpenERP v5
#class wizard_open_calling_partner(osv.osv_memory):
#    _inherit = "wizard.open.calling.partner"

#    def create_incoming_phonecall(self, cr, uid, ids, crm_categ, context=None):
#        '''Started by button on 'open calling partner wizard'''
#        partner_address = self.browse(cr, uid, ids[0], context=context).partner_address_id
#        action = self.pool.get('wizard.create.crm.phonecall')._create_open_crm_phonecall(cr, uid, partner_address, context=context)
#        return action

#wizard_open_calling_partner()
