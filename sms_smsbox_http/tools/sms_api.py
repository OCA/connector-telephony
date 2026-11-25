# Copyright 2026 INVITU (<https://www.invitu.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
import re

import requests

from odoo import _

from odoo.addons.sms_alternative_provider.models.sms_api import SmsApiBase

_logger = logging.getLogger(__name__)

SMSBOX_ERRORS = {
    "ERROR 01": "server_error",
    "ERROR 02": "unregistered",
    "ERROR 03": "insufficient_credit",
    "ERROR 04": "wrong_number_format",
    "ERROR 05": "server_error",
}


class SmsApiSmsboxHttp(SmsApiBase):
    KEY = "smsbox_http"
    NAME = "SMSBOX (HTTP API)"
    DESCRIPTION = "Send SMS with the SMSBOX HTTP API, using the linked IAP account."
    ENDPOINT = "https://api.smsbox.pro/1.1/api.php"
    TIMEOUT = 10
    PROVIDER_TO_SMS_FAILURE_TYPE = SmsApiBase.PROVIDER_TO_SMS_FAILURE_TYPE | {
        "insufficient_credit": "sms_credit",
        "unregistered": "sms_acc",
    }

    def __init__(self, env, account=None):
        super().__init__(env, account=account)
        self.account = account

    def _send_sms_batch(self, messages, delivery_reports_url=False):
        session = requests.Session()
        return [
            self._smsbox_send(session, message["content"], number_info)
            for message in messages
            for number_info in message["numbers"]
        ]

    def _smsbox_send(self, session, body, number_info):
        uuid = number_info["uuid"]
        if not number_info.get("number"):
            return {"uuid": uuid, "state": "sms_number_missing"}
        api_key = self.account.sms_smsbox_http_api_key if self.account else ""
        try:
            response = session.post(
                self.ENDPOINT,
                data=self._smsbox_prepare_data(body, number_info),
                headers={"Authorization": f"App {api_key}"},
                timeout=self.TIMEOUT,
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as error:
            _logger.warning("SMSBOX HTTP API error: %s", error)
            return {"uuid": uuid, "state": "server_error", "failure_reason": str(error)}
        answer = response.text.strip()
        if answer.startswith("OK"):
            return {
                "uuid": uuid,
                "state": "success",
                "sms_smsbox_http_reference": answer[2:].strip().split(",")[0],
            }
        return {
            "uuid": uuid,
            "state": SMSBOX_ERRORS.get(answer, "smsbox_http_error"),
            "failure_reason": answer,
        }

    def _smsbox_prepare_data(self, body, number_info):
        account = self.account
        data = {
            "dest": self._smsbox_format_number(number_info["number"]),
            "msg": body,
            "mode": account.sms_smsbox_http_mode,
            "strategy": account.sms_smsbox_http_strategy,
            "coding": "auto",
            "charset": "utf-8",
            "id": 1,
            "callback": 1,
            "cvar": f"odoo_uuid={number_info['uuid']}",
        }
        if account.sms_smsbox_http_mode == "Expert" and account.sms_smsbox_http_sender:
            data["origine"] = account.sms_smsbox_http_sender
        return data

    @staticmethod
    def _smsbox_format_number(number):
        # SMSBOX expects international numbers without "+" nor "00".
        number = re.sub(r"[^\d+]", "", number)
        if number.startswith("+"):
            return number[1:]
        if number.startswith("00"):
            return number[2:]
        return number

    def _get_sms_api_error_messages(self):
        error_messages = super()._get_sms_api_error_messages()
        error_messages.update(
            {
                "insufficient_credit": _("Insufficient SMSBOX credit."),
                "unregistered": _(
                    "Invalid SMSBOX API key, suspended key or unauthorized IP."
                ),
                "wrong_number_format": _("Invalid destination number."),
            }
        )
        return error_messages
