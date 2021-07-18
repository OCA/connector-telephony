# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json
import logging

import requests

from odoo import api, models

_logger = logging.getLogger(__name__)


class SmsApi(models.AbstractModel):

    _inherit = "sms.api"

    @api.model
    def _contact_iap(self, local_endpoint, params):

        account = self.env["iap.account"].get("sms.clickatell")
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": "VexvYSkCRPS_kQAghQUYOg==",
        }

        if local_endpoint == "/iap/message_send":
            messages = [
                {"channel": "sms", "to": number, "content": params["message"]}
                for number in params["numbers"]
            ]

        elif local_endpoint == "/iap/sms/1/send":
            messages = [
                {
                    "channel": "sms",
                    "to": params["number"],
                    "content": params["content"],
                }
                for message in params
            ]

        values = json.dumps({"messages": messages})
        request = requests.post(
            "https://platform.clickatell.com/v1/message", data=values, headers=headers
        )
        return  # request.json()
