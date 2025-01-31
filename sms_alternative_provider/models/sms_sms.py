# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

from odoo import fields, models


class SmsSms(models.Model):
    _inherit = "sms.sms"

    sms_gateway_id = fields.Many2one("ir.sms.gateway", string="SMS gateway used")

    def _postprocess_iap_sent_sms(
        self, iap_results, failure_reason=None, unlink_failed=False, unlink_sent=True
    ):
        """
        Group results by provider, let super handle actual iap results, divert others
        to their ir.sms.gateway handler
        """
        IrSmsGateway = self.env["ir.sms.gateway"]
        provider2results = {}
        for result in iap_results:
            provider2results.setdefault(
                IrSmsGateway.browse(result.get("sms_gateway_id", [])), []
            ).append(result)

        actual_iap_results = []
        for provider, results in provider2results.items():
            if not provider or provider.gateway_type == "iap":
                actual_iap_results.extend(results)
            else:
                provider._handle_results(
                    [], results, unlink_failed=unlink_failed, unlink_sent=unlink_sent
                )

        if actual_iap_results:
            return super()._postprocess_iap_sent_sms(
                actual_iap_results,
                failure_reason=failure_reason,
                unlink_failed=unlink_failed,
                unlink_sent=unlink_sent,
            )
