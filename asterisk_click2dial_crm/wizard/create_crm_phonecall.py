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

    def button_create_outgoing_phonecall(self, cr, uid, ids, context=None):
        partner_address = self.pool.get('res.partner.address').browse(cr, uid, context.get('partner_address_id'), context=context)
        return self._create_open_crm_phonecall(cr, uid, partner_address, crm_categ='Outbound', context=context)

    def _create_open_crm_phonecall(self, cr, uid, partner_address, crm_categ, context=None):
        if context is None:
            context = {}
        crm_phonecall_obj = self.pool.get('crm.phonecall')

        categ_ids = self.pool.get('crm.case.categ').search(cr, uid, [('name','=',crm_categ)], context={'lang': 'en_US'})
        case_section_ids = self.pool.get('crm.case.section').search(cr, uid, [('member_ids', 'in', uid)], context=context)
        values = {
            'name': _('Call with') + ' ' + partner_address.name,
            'partner_id': partner_address.partner_id and partner_address.partner_id.id or False,
            'partner_address_id': partner_address.id,
            'partner_phone': partner_address.phone,
            'partner_contact': partner_address.name,
            'partner_mobile': partner_address.mobile,
            'user_id': uid,
            'categ_id': categ_ids and categ_ids[0] or False,
            'section_id': case_section_ids and case_section_ids[0] or False,
            # As we now ask the user if he wants to create a phone call in CRM,
            # we suppose that he will decide to create one only if the call
            # has succeeded, so we create it directly in 'Held' (done) state.
            # Otherwise, it would have been created in 'Todo' (open) state.
            'state': 'done',
        }
        crm_phonecall_id = crm_phonecall_obj.create(cr, uid, values, context=context)

        return {
            'name': partner_address.name,
            'domain': [('partner_id', '=', partner_address.partner_id.id)],
            'res_model': 'crm.phonecall',
            'res_id': [crm_phonecall_id],
            'view_type': 'form',
            'view_mode': 'form,tree',
            'type': 'ir.actions.act_window',
            'nodestroy': False, # close the pop-up wizard after action
            'target': 'current',
            'context': context,
        }

wizard_create_crm_phonecall()


class wizard_open_calling_partner(osv.osv_memory):
    _inherit = "wizard.open.calling.partner"

    def create_incoming_phonecall(self, cr, uid, ids, crm_categ, context=None):
        '''Started by button on 'open calling partner wizard'''
        partner_address = self.browse(cr, uid, ids[0], context=context).partner_address_id
        action = self.pool.get('wizard.create.crm.phonecall')._create_open_crm_phonecall(cr, uid, partner_address, crm_categ='Inbound', context=context)
        return action

wizard_open_calling_partner()
