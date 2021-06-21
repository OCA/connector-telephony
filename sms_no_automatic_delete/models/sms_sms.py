# Copyright 2021 Akretion (https://www.akretion.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

from odoo import api, models


class SmsSms(models.Model):
    _inherit = "sms.sms"

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
