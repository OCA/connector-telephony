# Copyright 2023 ForgeFlow S.L. (https://www.forgeflow.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
import re

from odoo import _, api, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

try:
    from twilio.base.exceptions import TwilioRestException
except ImportError:
    _logger.error("Cannot import twilio", exc_info=True)


class SmsApi(models.AbstractModel):
    _inherit = "sms.api"

    def _get_twilio_sms_account(self):
        return self.env["iap.account"].search(
            [("provider", "=", "twilio"), ("service_name", "=", "sms")]
        )

    def _send_sms_with_twilio(self, number, message, sms_id):
        # Try to return same error code like odoo
        # list is here: self.IAP_TO_SMS_STATE
        if not number:
            return "wrong_number_format"
        try:
            account = self._get_twilio_sms_account()
            client = account.get_twilio_client(production=account.twilio_production_env)
            from_phone = account.twilio_number_id
            from_number = "+" + re.sub("[^0-9]", "", from_phone.phone_number)
            number = "+" + re.sub("[^0-9]", "", number)
            client.messages.create(to=number, from_=from_number, body=message)
        except TwilioRestException as e:
            self.env["sms.sms"].browse(sms_id).error_detail = e.msg
            raise UserError(e.msg) from e
        return "success"

    @api.model
    def _send_sms(self, numbers, message):
        if self._get_twilio_sms_account():
            # This method seem to be deprecated (no odoo code use it)
            # as Twilio do not support it we do not support it
            # Note: if you want to implement it becareful just looping
            # on the list of number is not the right way to do it.
            # If you have an error, you will send and send again the same
            # message
            raise NotImplementedError
        else:
            return super()._send_sms(numbers, message)

    @api.model
    def _send_sms_batch(self, messages):
        if self._get_twilio_sms_account():
            if len(messages) != 1:
                # we already have inherited the split_batch method on sms.sms
                # so this case should not append
                raise UserError(_("Batch sending is not supported with Twilio"))
            state = self._send_sms_with_twilio(
                messages[0]["number"], messages[0]["content"], messages[0]["res_id"]
            )
            return [{"state": state, "credit": 0, "res_id": messages[0]["res_id"]}]
        else:
            return super()._send_sms_batch(messages)
