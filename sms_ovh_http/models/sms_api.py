# Copyright 2020 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


import requests

from odoo import _, api, models
from odoo.exceptions import UserError

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

    def _get_sms_account(self):
        return self.env["iap.account"].get("sms")

    def _send_sms_with_ovh_http(self, number, message):
        account = self._get_sms_account()
        r = requests.get(
            OVH_HTTP_ENDPOINT,
            params=self._prepare_ovh_http_params(account, number, message),
        )
        response = r.text
        if response[0:2] != "OK":
            raise ValueError(response)

    def _is_sent_with_ovh(self):
        return self._get_sms_account().provider == "sms_ovh_http"

    @api.model
    def _send_sms(self, number, message):
        if self._is_sent_with_ovh():
            self._send_sms_with_ovh_http(number, message)
        else:
            return super()._send_sms(number, message)

    @api.model
    def _send_sms_batch(self, messages):
        if self._is_sent_with_ovh():
            if len(messages) != 1:
                # we already have inherited the split_batch method on sms.sms
                # so this case shouldsnot append
                raise UserError(_("Batch sending is not support with OVH"))
            self._send_sms(messages[0]["number"], messages[0]["content"])
            return [{"state": "success", "credit": 0, "res_id": messages[0]["res_id"]}]
        else:
            return super()._send_sms_batch(messages)
