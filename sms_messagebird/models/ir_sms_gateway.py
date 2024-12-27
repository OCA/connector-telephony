# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

import logging

import requests

from odoo import fields, models

_logger = logging.getLogger(__name__)


class IrSmsGateway(models.Model):

    _inherit = "ir.sms.gateway"

    gateway_type = fields.Selection(
        selection_add=[("messagebird", "Messagebird")],
        ondelete={"messagebird": "cascade"},
    )
    messagebird_apikey = fields.Char("API key")

    def _send_messagebird(self, messages):
        apikey = self.messagebird_apikey
        result = []
        for message in messages:
            # TODO: use batch api
            response = requests.post(
                "https://rest.messagebird.com/messages",
                headers={
                    "Authorization": "AccessKey %s" % apikey,
                },
                data={
                    "originator": self.env.user.company_id.phone
                    or self.env.user.company_id.name[:11],
                    "recipients": message["number"],
                    "body": message["content"],
                },
                timeout=100,
            )
            data = response.json()
            _logger.debug(data)
            if data.get("errors"):
                _logger.error(data["errors"])
                result.append(
                    {
                        "id": message.get("id"),
                        "state": "error",
                        "failure_type": "sms_server",
                    }
                )
            else:
                result.append(
                    {
                        "id": message.get("id"),
                        "state": "sent",
                    }
                )
        return result
