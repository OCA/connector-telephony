# Copyright 2014-2018 Akretion France
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import _, api, models

from odoo.addons.web.controllers.utils import clean_action

logger = logging.getLogger(__name__)


class PhoneCommon(models.AbstractModel):
    _inherit = "phone.common"

    @api.model
    def _prepare_incall_pop_action(self, record_res, number):
        action = False
        if record_res:
            obj = self.env[record_res[0]]
            action = {
                "name": obj._description,
                "type": "ir.actions.act_window",
                "res_model": record_res[0],
                "view_mode": "form,tree",
                "views": [[False, "form"]],
                "res_id": record_res[1],
            }
        else:
            action = {
                "name": _("Number Not Found"),
                "type": "ir.actions.act_window",
                "res_model": "number.not.found",
                "view_mode": "form",
                "views": [[False, "form"]],
                "context": {"default_calling_number": number},
            }
        return action

    @api.model
    def incall_notify_by_login(self, number, login_list):
        assert isinstance(login_list, list), "login_list must be a list"
        res = self.get_record_from_phone_number(number)
        users = self.env["res.users"].search([("login", "in", login_list)])
        logger.info(
            f"Notify incoming call from number {number} to user IDs {users.ids}"
        )
        action = self._prepare_incall_pop_action(res, number)
        action = clean_action(action, self.env)
        if action:
            for user in users:
                channel_partner = self.env.user.partner_id
                bus_message = {
                    "type": "success",
                    "message": _("Here is my message"),
                    "title": _("Incoming call"),
                    "action": action,
                    "action_link_name": "action_link_name",
                }
                self.sudo().env["bus.bus"]._sendone(
                    channel_partner, "web.notify", [bus_message]
                )
                logger.debug(f"This action has been sent to user ID {user.id} {action}")
        if res:
            callerid = res[2]
        else:
            callerid = False
        return callerid
