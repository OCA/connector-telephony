# -*- encoding: utf-8 -*-
##############################################################################
#
#    Asterisk click2dial CRM module for OpenERP
#    Copyright (c) 2011 Zikzakmedia S.L. (http://zikzakmedia.com)
#    Copyright (c) 2012-2013 Akretion (http://www.akretion.com)
#    Copyright (C) 2013 Invitu <contact@invitu.com>
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
# Lib to translate error messages
from openerp.tools.translate import _


class res_partner(osv.osv):
    _name = 'res.partner'
    _inherit = ['res.partner', 'asterisk.common']

    def action_dial(self, cr, uid, ids, context=None):
        '''
        This method open the phone call history when the phone click2dial
        button of asterisk_click2dial module is pressed
        :return the phone call history view of the partner
        '''
        if context is None:
            context = {}
        super(res_partner, self).action_dial(cr, uid, ids, context=context)
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
    _name = 'crm.lead'
    _inherit = ['crm.lead', 'asterisk.common']


    def create(self, cr, uid, vals, context=None):
        vals_reformated = self._generic_reformat_phonenumbers(cr, uid, vals, context=context)
        return super(crm_lead, self).create(cr, uid, vals_reformated, context=context)


    def write(self, cr, uid, ids, vals, context=None):
        vals_reformated = self._generic_reformat_phonenumbers(cr, uid, vals, context=context)
        return super(crm_lead, self).write(cr, uid, ids, vals_reformated, context=context)

