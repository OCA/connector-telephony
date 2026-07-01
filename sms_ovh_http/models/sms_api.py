# Copyright 2020 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


import ovh

from odoo import _, api, models
from odoo.exceptions import UserError

OVH_API_ENDPOINT = "ovh-eu"


class SmsApi(models.AbstractModel):
    _inherit = "sms.api"

    def _get_sms_account(self):
        return self.env["iap.account"].get("sms").exists()

    def _send_sms_with_ovh_api(self, number, message, sms_id):
        if not number:
            return "wrong_number_format"
        account = self._get_sms_account()
        client = ovh.Client(
            endpoint=OVH_API_ENDPOINT,
            application_key=account.sms_ovh_http_app_key,
            application_secret=account.sms_ovh_http_app_secret,
            consumer_key=account.sms_ovh_http_consumer_key,
        )
        try:
            client.post(
                "/sms/%s/jobs" % account.sms_ovh_http_service_name,
                message=message,
                sender=account.sms_ovh_http_from,
                receivers=[number],
                noStopClause=True,
            )
            return "success"
        except ovh.exceptions.APIError as e:
            self.env["sms.sms"].browse(sms_id).error_detail = str(e)
            return "server_error"

    def _is_sent_with_ovh(self):
        return self._get_sms_account().provider == "sms_ovh_http"

    @api.model
    def _send_sms(self, numbers, message):
        if self._is_sent_with_ovh():
            raise NotImplementedError
        else:
            return super()._send_sms(numbers, message)

    @api.model
    def _send_sms_batch(self, messages):
        if self._is_sent_with_ovh():
            if len(messages) != 1:
                raise UserError(_("Batch sending is not supported with OVH"))
            msg = messages[0]
            state = self._send_sms_with_ovh_api(
                msg["number"], msg["content"], msg["res_id"]
            )
            return [{"state": state, "credit": 0, "res_id": msg["res_id"]}]
        else:
            return super()._send_sms_batch(messages)
