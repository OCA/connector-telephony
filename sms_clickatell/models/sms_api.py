# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json

import requests

from odoo import api, models


class Clickatell(object):
    # _name = "clickatell.sdk"
    # _description = "Clickatell SDK to send SMS"

    def __init__(self, key):
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": key,
        }

    def send_message(self, params):
        values = json.dumps({"messages": [params]})
        request = requests.post(
            "https://platform.clickatell.com/v1/message",
            data=values,
            headers=self.headers,
        )
        return request.json()


class SmsApi(models.AbstractModel):

    _inherit = "sms.api"

    def _send_sms_clickatell(self, sms, params):
        return sms.send_message(params)

    @api.model
    def _send_sms(self, numbers, message):
        account = self.env["iap.account"].get("nexmo.sms")
        if not account:
            return super(SmsApi, self)._send_sms(numbers, message)
        sms = Clickatell(key=account.key)
        self._send_sms_clickatell(
            sms, {"channel": "sms", "to": numbers, "content": message},
        )

    @api.model
    def _send_sms_batch(self, messages):
        account = self.env["iap.account"].get("nexmo.sms")
        if not account:
            return super(SmsApi, self)._send_sms_batch(messages)

        sms = Clickatell(key=account.key)

        for record in messages:
            result = self._send_sms_clickatell(
                sms,
                {
                    "channel": "sms",
                    "to": record["number"],
                    "content": record["content"],
                },
            )
            if result["messages"][0]["status"] == "0":
                record["state"] = "success"
            else:
                record["state"] = "error"
        return messages
