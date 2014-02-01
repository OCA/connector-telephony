# -*- coding: utf-8 -*-
##############################################################################
#
#    Asterisk Pop-up module for OpenERP
#    Copyright (C) 2014 Alexis de Lattre <alexis@via.ecp.fr>
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

from openerp.osv import orm, fields
import logging

logger = logging.getLogger(__name__)


class res_partner(orm.Model):
    _inherit = 'res.partner'

    def _prepare_incall_pop_action(
            self, cr, uid, partner_res, number, context=None):
        if partner_res:
            action = {
                'name': 'Partner',
                'type': 'ir.actions.act_window',
                'res_model': 'res.partner',
                'view_type': 'form',
                'view_mode': 'form,tree,kanban',
                'views': [[False, 'form']],  # Beurk, but needed
                'target': 'new',
                'res_id': partner_res[0],
                }
        else:
            action = {
                'name': 'No Partner Found',
                'type': 'ir.actions.act_window',
                'res_model': 'wizard.open.calling.partner',
                'view_type': 'form',
                'view_mode': 'form',
                'views': [[False, 'form']],  # Beurk, but needed
                'target': 'new',
                'context': {'incall_number_popup': number}
                }
        return action

    def incall_notify_by_login(
            self, cr, uid, number, login_list, context=None):
        assert isinstance(login_list, list), 'login_list must be a list'
        res = self.get_partner_from_phone_number(
            cr, uid, number, context=context)
        user_ids = self.pool['res.users'].search(
            cr, uid, [('login', 'in', login_list)], context=context)
        logger.debug(
            'Notify incoming call from number %s to users %s'
            % (number, user_ids))
        action = self._prepare_incall_pop_action(
            cr, uid, res, number, context=context)
        if action:
            users = self.pool['res.users'].read(
                cr, uid, user_ids, ['context_incall_popup'], context=context)
            for user in users:
                if user['context_incall_popup']:
                    self.pool['action.request'].notify(
                        cr, uid, to_id=user['id'], **action)
                    logger.debug(
                        'This action has been sent to user ID %d: %s'
                        % (user['id'], action))
        return res


class res_users(orm.Model):
    _inherit = 'res.users'

    _columns = {
        'context_incall_popup': fields.boolean('Pop-up on Incoming Calls'),
        }

    _defaults = {
        'context_incall_popup': True,
        }
