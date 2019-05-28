# -*- coding: utf-8 -*-
# Copyright 2014-2018 Akretion France
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, _
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
                'views': [[False, 'form']],
                'res_id': record_res[1],
                }
        else:
            action = {
                'name': _('Number Not Found'),
                'type': 'ir.actions.act_window',
                'res_model': 'number.not.found',
                'view_mode': 'form',
                'views': [[False, 'form']],
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
        logger.info(
            'Notify incoming call from number %s to users IDs %s'
            % (number, users.ids))
        action = self._prepare_incall_pop_action(res, number)
        if action:
            title = _('Incoming call')
            message = _('Call from %s') % number
            action_link_name = res and res[2] or action['name']
            users.notify_info(
                message, title=title, sticky=True, action=action,
                action_link_name=action_link_name)
            logger.debug(
                'This action has been sent to users IDs %s: %s'
                % (users.ids, action))
        if res:
            callerid = res[2]
        else:
            callerid = False
        return callerid
