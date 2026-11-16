# Copyright 2026 INVITU (<https://www.invitu.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models

from ..tools.sms_api import SmsApiSmsboxHttp


class SmsSms(models.Model):
    _inherit = "sms.sms"

    def _get_batch_size(self):
        # One HTTP call per number: keep transactions short.
        if set(self.sms_gateway_id.mapped("gateway_type")) == {SmsApiSmsboxHttp.KEY}:
            return 10
        return super()._get_batch_size()

    def _handle_call_result_hook(self, results):
        references = {
            result["uuid"]: result["sms_smsbox_http_reference"]
            for result in results
            if result.get("sms_smsbox_http_reference")
        }
        for sms in self.filtered(lambda sms: sms.uuid in references):
            sms.sms_tracker_id.sms_smsbox_http_reference = references[sms.uuid]
        return super()._handle_call_result_hook(results)
