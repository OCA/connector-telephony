# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json

import requests

from odoo import api, models


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
            messages = [
                {"channel": "sms", "to": number, "content": params["message"]}
                for number in params["numbers"]
            ]

        elif local_endpoint == "/iap/sms/1/send":
            messages = [
                {
                    "channel": "sms",
                    "to": message["number"],
                    "content": message["content"],
                }
                for message in params["messages"]
            ]

        values = json.dumps({"messages": messages})
        request = requests.post(
            "https://platform.clickatell.com/v1/message", data=values, headers=headers
        )
        response_list = request.json()["messages"]
        params_list = params["messages"]
        if type(request.json()) is dict:
            response = []
            for resp_id in range(len(response_list)):
                response.append(
                    {
                        **params_list[resp_id],
                        "state": (
                            "success"
                            if "error" not in response_list[resp_id]
                            else "wrong_number_format"
                        ),
                        "credit": 2,
                        **response_list[resp_id],
                    }
                )
        return response
