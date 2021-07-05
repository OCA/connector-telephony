# Copyright 2021 Akretion (https://www.akretion.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

from odoo import api, models


class SmsSms(models.Model):
    _inherit = "sms.sms"

    @api.model
    def _postprocess_iap_sent_sms(
        self, iap_results, failure_reason=None, delete_all=False
    ):
        # Update state of the sms as "sent" when they are sent.
        ids = [item["res_id"] for item in iap_results if item["state"] == "success"]
        self.browse(ids).write({"state": "sent"})
        return super()._postprocess_iap_sent_sms(
            iap_results, failure_reason=failure_reason, delete_all=delete_all
        )

    @api.model
    def _purge(self, days):
        sms = self.env["sms.sms"].search(
            [("write_date", "<=", datetime.now() - timedelta(days=days))]
        )
        sms.with_context(force_unlink=True).unlink()

    def unlink(self):
        if self._context.get("force_unlink"):
            return super().unlink()
        else:
            return True
