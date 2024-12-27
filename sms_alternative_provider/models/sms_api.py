# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

from odoo import api, models


class SmsApi(models.AbstractModel):
    _inherit = "sms.api"

    @api.model
    def _send_sms_batch(self, messages):
        """
        Divert SMS sending to the gateway model if not asked not to
        """
        if self.env.context.get("force_iap"):
            return super()._send_sms_batch(messages)
        return self.env["ir.sms.gateway"]._send(
            [dict(message, id=message.get("res_id")) for message in messages],
            handle_results=False,
        )
