# -*- coding: utf-8 -*-
# © 2014-2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, _
import logging


logger = logging.getLogger(__name__)


class PhoneCommon(models.AbstractModel):
    _inherit = 'phone.common'

    @api.model
    def _prepare_incall_pop_action(self, record_res, number):
        action = False
        if record_res:
            obj = self.env[record_res[0]]
            action = {
                'name': obj._description,
                'type': 'ir.actions.act_window',
                'res_model': record_res[0],
                'view_mode': 'form,tree',
                'views': [[False, 'form']],  # Beurk, but needed
                'target': 'new',
                'res_id': record_res[1],
                }
        else:
            action = {
                'name': _('Number Not Found'),
                'type': 'ir.actions.act_window',
                'res_model': 'number.not.found',
                'view_mode': 'form',
                'views': [[False, 'form']],  # Beurk, but needed
                'target': 'new',
                'context': {'default_calling_number': number}
            }
        return action

    @api.model
    def incall_notify_by_login(self, number, login_list):
        assert isinstance(login_list, list), 'login_list must be a list'
        res = self.get_record_from_phone_number(number)
        users = self.env['res.users'].search(
            [('login', 'in', login_list)])
        logger.debug(
            'Notify incoming call from number %s to users %s'
            % (number, users.ids))
        action = self._prepare_incall_pop_action(res, number)
        if action:
            for user in users:
                if user.context_incall_popup:
                    self.sudo(user.id).env['action.request'].notify(action)
                    logger.debug(
                        'This action has been sent to user ID %d: %s'
                        % (user.id, action))
        if res:
            callerid = res[2]
        else:
            callerid = False
        return callerid

    @api.model
    def incall_notify_by_extension(self, number, extension_list):
        assert isinstance(extension_list, list), \
            'extension_list must be a list'
        res = self.get_record_from_phone_number(number)
        users = self.env['res.users'].search(
            [('internal_number', 'in', extension_list)])
        logger.debug(
            'Notify incoming call from number %s to users %s'
            % (number, users.ids))
        action = self._prepare_incall_pop_action(res, number)
        if action:
            for user in users:
                if user.context_incall_popup:
                    self.sudo(user.id).env['action.request'].notify(action)
                    logger.debug(
                        'This action has been sent to user ID %d: %s'
                        % (user.id, action))
        if res:
            callerid = res[2]
        else:
            callerid = False
        return callerid


class ResUsers(models.Model):
    _inherit = 'res.users'

    context_incall_popup = fields.Boolean(
        string='Pop-up on Incoming Calls', default=True)
