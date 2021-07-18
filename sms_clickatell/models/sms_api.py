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
            "Authorization": account.key,
        }

        if local_endpoint == "/iap/message_send":
            """Send a single message to several numbers

            :param numbers: list of E164 formatted phone numbers
            :param message: content to send

            :raises ? TDE FIXME
            """
            messages = [
                {"channel": "sms", "to": number, "content": params["message"]}
                for number in params["numbers"]
            ]

        elif local_endpoint == "/iap/sms/1/send":
            """Send SMS using IAP in batch mode

            :param messages: list of SMS to send, structured as dict [{
                'res_id':  integer: ID of sms.sms,
                'number':  string: E164 formatted phone number,
                'content': string: content to send
            }]

            :return: return of /iap/sms/1/send controller which is a list of dict [{
                'res_id': integer: ID of sms.sms,
                'state':  string: 'insufficient_credit' or
                        'wrong_number_format' or 'success',
                'credit': integer: number of credits spent to send this SMS,
            }]

            :raises: normally none
            """
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
            "https://platform.clickatell.com/v1/message", data=values, headers=headers,
        )
        return request.json()
