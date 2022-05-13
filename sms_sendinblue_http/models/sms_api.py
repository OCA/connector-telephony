# Copyright 2022 Moka Tourisme (https://www.mokatourisme.fr).
# @author Pierre Verkest <pierreverkest84@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

import requests

from odoo import _, api, models
from odoo.exceptions import UserError

SENDINBLUE_HTTP_ENDPOINT = "https://api.sendinblue.com/v3/transactionalSMS/sms"


_logger = logging.getLogger(__name__)


class SmsApi(models.AbstractModel):
    _inherit = "sms.api"

    def _get_sms_account(self):
        return self.env["iap.account"].get("sms")

    def _send_sms_with_sendinblue_http(self, number, message, sms_id):
        if not number:
            return "wrong_number_format", -1

        account = self._get_sms_account()

        payload = {
            "type": "transactional",
            "unicodeEnabled": False,
            "recipient": number,
            "sender": account.sms_sendinblue_http_from,
            "content": message,
            # "tag": "tag",
            # "webUrl": "https://myWebHookTriger"
        }

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "api-key": account.sms_sendinblue_http_api_key,
        }

        # SENDINBLUE API DOC https://developers.sendinblue.com/reference/sendtransacsms
        response = requests.post(
            SENDINBLUE_HTTP_ENDPOINT, json=payload, headers=headers
        )
        _logger.debug(
            "Sendinblue (HTTP code %s) response: %s - send: %s",
            response.status_code,
            response.text,
            payload,
        )
        res = response.json()
        if str(response.status_code) != "201":
            self.env["sms.sms"].browse(sms_id).error_detail = res.get("message")
            state = res.get("code")
            state = (
                state
                if state in self.env["sms.sms"].IAP_TO_SMS_STATE.keys()
                else "server_error"
            )
            return state, -1

        return "success", res.get("remainingCredits", 0)

    def _is_sent_with_sendinblue(self):
        return self._get_sms_account().provider == "sms_sendinblue_http"

    @api.model
    def _send_sms(self, numbers, message):
        if self._is_sent_with_sendinblue():
            # This method seem to be deprecated (no odoo code use it)
            # as SENDINBLUE do not support it we do not support it
            # Note: if you want to implement it becarefull just looping
            # on the list of number is not the right way to do it.
            # If you have an error, you will send and send again the same
            # message
            raise NotImplementedError
        else:
            return super()._send_sms(numbers, message)

    @api.model
    def _send_sms_batch(self, messages):
        if self._is_sent_with_sendinblue():
            if len(messages) != 1:
                # we already have inherited the split_batch method on sms.sms
                # so this case shouldsnot append
                raise UserError(
                    _(
                        "Batch sending is not implemented by this module sms_sendinblue_http"
                    )
                )
            state, credit = self._send_sms_with_sendinblue_http(
                messages[0]["number"], messages[0]["content"], messages[0]["res_id"]
            )
            return [{"state": state, "credit": credit, "res_id": messages[0]["res_id"]}]
        else:
            return super()._send_sms_batch(messages)

    @api.model
    def _get_sms_api_error_messages(self):
        """used by mass_mailing_sms module in test operation"""
        res = super()._get_sms_api_error_messages()
        res.update(
            {
                "not_enough_credits": res["insufficient_credit"],
                "unauthorized": _("Unauthorized Sendinblue account."),
                "invalid_parameter": _("Invalid parameter"),
                "missing_parameter": _("Missing parameter"),
                "out_of_range": _("Out of range"),
                "campaign_processing": _("Campaign processing"),
                "campaign_sent": _("Campaign sent"),
                "document_not_found": _("Document not found"),
                "reseller_permission_denied": _("Reseller permission denied"),
                "permission_denied": _("Permission denied"),
                "duplicate_parameter": _("Duplicate parameter"),
                "duplicate_request": _("Duplacate request"),
                "method_not_allowed": _("Method not allowed"),
                "account_under_validation": _("Account under validation"),
                "not_acceptable": _("Not acceptable"),
            }
        )
        return res
