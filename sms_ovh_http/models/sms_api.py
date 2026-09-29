# Copyright 2020 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


import requests

from odoo import _
from odoo.exceptions import UserError

from odoo.addons.sms.tools.sms_api import (
    SmsApi as OdooSmsApi,
)
from odoo.addons.sms_alternative_provider.models.sms_api import SmsApiBase

OVH_HTTP_ENDPOINT = "https://www.ovh.com/cgi-bin/sms/http2sms.cgi"


class OvhSmsApi(SmsApiBase, OdooSmsApi):
    KEY = "ovh"
    NAME = "OVH IAP"
    DESCRIPTION = "Send sms through OVH IAP"
    HTTP_TIMEOUT = 10

    def _contact_iap(self, local_endpoint, params, timeout=15):
        return ""

    def _send_sms_batch(
        self, messages, delivery_reports_url=False
    ):  # TODO RIGR: switch to kwargs in master
        if self._is_sent_with_ovh():
            if len(messages) != 1:
                # we already have inherited the split_batch method on sms.sms
                # so this case shouldsnot append
                raise UserError(_("Batch sending is not support with OVH"))
            state = self._send_sms_with_ovh_http(
                messages[0]["numbers"][0]["number"],
                messages[0]["content"],
                messages[0]["numbers"][0]["uuid"],
            )
            return [
                {"state": state, "credit": 0, "uuid": messages[0]["numbers"][0]["uuid"]}
            ]
        else:
            return super()._send_sms_batch(messages)

    def _prepare_ovh_http_params(self, account, number, message):
        return {
            "smsAccount": account.sms_ovh_http_account,
            "login": account.sms_ovh_http_login,
            "password": account.sms_ovh_http_password,
            "from": account.sms_ovh_sender_name,
            "to": number,
            "message": message,
            "noStop": 1,
        }

    def _get_sms_account(self):
        return self.env["iap.account"].get("sms").exists()

    def _send_sms_with_ovh_http(self, number, message, uuid):
        # Try to return same error code like odoo
        # list is here: self.IAP_TO_SMS_STATE
        if not number:
            return "wrong_number_format"
        account = self.account
        r = requests.get(
            OVH_HTTP_ENDPOINT,
            params=self._prepare_ovh_http_params(account, number, message),
            timeout=self.HTTP_TIMEOUT,
        )
        response = r.text
        if response[0:2] != "OK":
            self.env["sms.sms"].search([("uuid", "=", uuid)])[
                0
            ].error_detail = response[3:]
            return "server_error"
        return "success"

    def _is_sent_with_ovh(self):
        return self.account.provider == "sms_ovh_http"
