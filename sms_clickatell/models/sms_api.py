# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json
import logging

import requests

from odoo import api, models

_logger = logging.getLogger(__name__)


class Clickatell(object):
    # _name = "clickatell.sdk"
    """Clickatell SDK to send SMS"""

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
        """Send a single message to several numbers

        :param numbers: list of E164 without + formatted phone numbers
        (what standard is it?)
        :param message: content to send

        :raises ? TDE FIXME
        """
        account = self.env["iap.account"].get("clickatell.sms")
        _logger.warning("account %s", account)
        if not account:
            return super(SmsApi, self)._send_sms(numbers, message)
        sms = Clickatell(key=account.key)
        numbers = [number[1:] for number in numbers]
        for number in numbers:
            self._send_sms_clickatell(
                sms, {"channel": "sms", "to": number, "content": message},
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
                    "to": record["number"][1:],
                    "content": record["content"],
                },
            )
            if result["messages"][0]["status"] == "0":
                record["state"] = "success"
            else:
                record["state"] = "error"
        return messages
