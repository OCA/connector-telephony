# Copyright 2023 ForgeFlow S.L. (https://www.forgeflow.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
import re

from odoo.exceptions import UserError

from odoo.addons.sms.tools.sms_api import SmsApi

_send_sms_batch_original = SmsApi._send_sms_batch

_logger = logging.getLogger(__name__)

try:
    from twilio.base.exceptions import TwilioRestException
except ImportError:
    _logger.error("Cannot import twilio", exc_info=True)


class TwilioSmsApi(SmsApi):
    def _get_twilio_sms_account(self):
        return self.env["iap.account"].search(
            [
                ("provider", "=", "twilio"),
                ("service_name", "=", "sms"),
                "|",
                ("company_ids", "in", self.env.companies.ids),
                ("company_ids", "=", False),
            ],
            limit=1,
        )

    def _send_sms_with_twilio(self, account, number, message, sms_uuid):
        # Try to return same error code like odoo
        # list is here: self.IAP_TO_SMS_STATE
        if not number:
            return "wrong_number_format"
        try:
            client = account.get_twilio_client(production=account.twilio_production_env)
            from_phone = account.twilio_number_id
            from_number = "+" + re.sub("[^0-9]", "", from_phone.phone_number)
            number = "+" + re.sub("[^0-9]", "", number)
            client.messages.create(to=number, from_=from_number, body=message)
        except TwilioRestException as e:
            self.env["sms.sms"].sudo().search(
                [("uuid", "=", sms_uuid)]
            ).error_detail = e.msg
            raise UserError(e.msg) from e
        return "success"

    def _send_sms_batch(self, messages, delivery_reports_url=False):
        account = TwilioSmsApi._get_twilio_sms_account(self)
        if account:
            if len(messages) != 1:
                # we already have inherited the split_batch method on sms.sms
                # so this case should not append
                raise UserError(
                    self.env._("Batch sending is not supported with Twilio")
                )
            state = TwilioSmsApi._send_sms_with_twilio(
                self,
                account,
                messages[0]["numbers"][0]["number"],
                messages[0]["content"],
                messages[0]["numbers"][0]["uuid"],
            )
            return [
                {"state": state, "credit": 0, "uuid": messages[0]["numbers"][0]["uuid"]}
            ]
        else:
            return _send_sms_batch_original(self, messages, delivery_reports_url)


SmsApi._send_sms_batch = TwilioSmsApi._send_sms_batch
