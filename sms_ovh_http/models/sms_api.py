# Copyright 2020 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


import requests

from odoo import api, models

OVH_HTTP_ENDPOINT = "https://www.ovh.com/cgi-bin/sms/http2sms.cgi"


class SmsApi(models.AbstractModel):
    _inherit = "sms.api"

    def _prepare_ovh_http_params(self, account, number, message):
        return {
            "smsAccount": account.sms_ovh_http_account,
            "login": account.sms_ovh_http_login,
            "password": account.sms_ovh_http_password,
            "from": account.sms_ovh_http_from,
            "to": number,
            "message": message,
            "noStop": 1,
        }

    def _send_sms_with_ovh_http(self, account, number, message):
        r = requests.get(
            OVH_HTTP_ENDPOINT,
            params=self._prepare_ovh_http_params(account, number, message),
        )
        response = r.text
        if response[0:2] != "OK":
            raise ValueError(response)

    @api.model
    def _send_sms(self, number, message):
        account = self.env["iap.account"].get("sms")
        if account.provider == "sms_ovh_http":
            self._send_sms_with_ovh_http(account, number, message)
        else:
            return super()._send_sms(number, message)
