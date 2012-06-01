# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2011 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
#                       Jesús Martín <jmartin@zikzakmedia.com>
#    $Id$
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
    _name = "res.partner.address"
    _inherit = "res.partner.address"

    def action_dial_phone(self, cr, uid, ids, context=None):
        '''
        This method open the phone call history when the phone click2dial
        button of asterisk_click2dial module is pressed
        :return the phone call history view of the partner
        '''
        if context is None:
            context = {}
        super(res_partner_address, self).action_dial_phone(cr, uid, ids, context)
        crm_phonecall_id = self.create_phonecall(cr, uid, ids, context)
        partner = self.browse(cr, uid, ids[0], context).partner_id
        return {
            'name': partner.name,
            'domain': "[('partner_address_id.partner_id.id', '=', %s)]" % partner.id,
            'res_model': 'crm.phonecall',
            'res_id': crm_phonecall_id,
            'view_type': 'form',
            'view_mode': 'form,tree',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'context': context,
        }

    def action_dial_mobile(self, cr, uid, ids, context=None):
        '''
        This method open the phone call history when the mobile click2dial
        button of asterisk_click2dial module is pressed
        :return the phone call history view of the partner
        '''
        if context is None:
            context = {}
        super(res_partner_address, self).action_dial_mobile(cr, uid, ids, context)
        crm_phonecall_id = self.create_phonecall(cr, uid, ids, context)
        partner = self.browse(cr, uid, ids[0], context).partner_id
        return {
            'name': partner.name,
            'domain': "[('partner_address_id.partner_id.id', '=', %s)]" % partner.id,
            'res_model': 'crm.phonecall',
            'res_id': crm_phonecall_id,
            'view_type': 'form',
            'view_mode': 'form,tree',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'context': context,
        }

    def create_phonecall(self, cr, uid, ids, context = None):
        '''
        This method creates a phone call history when the phone click2dial
        button of asterisk_click2dial module is pressed and opens it.
        :return True
        '''
        if context is None:
            context = {}

        crm_phonecall_obj = self.pool.get('crm.phonecall')
        partner_address = self.browse(cr, uid, ids[0], context)

        categ_ids = self.pool.get('crm.case.categ').search(cr, uid, [('name','=','Outbound')], context={'lang': 'en_US'})
        case_seccion_ids = self.pool.get('crm.case.section').search(cr, uid, [('member_ids', 'in', uid)], context = context)
        values = {
            'name': "",
            'partner_id': partner_address.partner_id and partner_address.partner_id.id or False,
            'partner_address_id': partner_address.id,
            'partner_phone': partner_address.phone,
            'partner_contact': partner_address.name,
            'partner_mobile': partner_address.mobile,
            'user_id': uid,
            'categ_id': categ_ids and categ_ids[0] or False,
            'section_id': case_seccion_ids and case_seccion_ids[0] or False,
        }
        crm_phonecall_id = crm_phonecall_obj.create(cr, uid, values, context)
        return crm_phonecall_id

res_partner_address()
