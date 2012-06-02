# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
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

class res_partner_address(osv.osv):
    _inherit = "res.partner.address"

    def dial(self, cr, uid, ids, phone_field='phone', context=None):
        '''
        This method open the phone call history when the phone click2dial
        button of asterisk_click2dial module is pressed
        :return the phone call history view of the partner
        '''
        if context is None:
            context = {}
        super(res_partner_address, self).dial(cr, uid, ids, phone_field=phone_field, context=context)
        return self.create_open_phonecall(cr, uid, ids, crm_categ='Outbound', context=context)


    def create_open_phonecall(self, cr, uid, ids, crm_categ, context=None):
        if context is None:
            context = {}
        crm_phonecall_id = self.create_phonecall(cr, uid, ids, crm_categ=crm_categ, context=context)
        partner = self.browse(cr, uid, ids[0], context=context).partner_id
        return {
            'name': partner.name,
            'domain': "[('partner_address_id.partner_id.id', '=', %s)]" % partner.id,
            'res_model': 'crm.phonecall',
            'res_id': [crm_phonecall_id],
            'view_type': 'form',
            'view_mode': 'form,tree',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'context': context,
        }


    def create_phonecall(self, cr, uid, ids, crm_categ='Outbound', context=None):
        '''
        This method creates a phone call history when the phone click2dial
        button of asterisk_click2dial module is pressed and opens it.
        :return True
        '''
        if context is None:
            context = {}

        crm_phonecall_obj = self.pool.get('crm.phonecall')
        partner_address = self.browse(cr, uid, ids[0], context=context)

        categ_ids = self.pool.get('crm.case.categ').search(cr, uid, [('name','=',crm_categ)], context={'lang': 'en_US'})
        case_section_ids = self.pool.get('crm.case.section').search(cr, uid, [('member_ids', 'in', uid)], context=context)
        values = {
            'name': "CRM Call", # TODO check name
            'partner_id': partner_address.partner_id and partner_address.partner_id.id or False,
            'partner_address_id': partner_address.id,
            'partner_phone': partner_address.phone,
            'partner_contact': partner_address.name,
            'partner_mobile': partner_address.mobile,
            'user_id': uid,
            'categ_id': categ_ids and categ_ids[0] or False,
            'section_id': case_section_ids and case_section_ids[0] or False,
        }
        crm_phonecall_id = crm_phonecall_obj.create(cr, uid, values, context=context)
        return crm_phonecall_id

res_partner_address()

class wizard_open_calling_partner(osv.osv_memory):
    _inherit = "wizard.open.calling.partner"

    def create_incoming_phonecall(self, cr, uid, ids, crm_categ, context=None):
        '''Started by button on 'open calling partner wizard'''
        partner_address_id = self.browse(cr, uid, ids[0], context=context).partner_address_id.id
        action = self.pool.get('res.partner.address').create_open_phonecall(cr, uid, [partner_address_id], crm_categ='Inbound', context=context)
        action['nodestroy'] = False
        return action

wizard_open_calling_partner()
