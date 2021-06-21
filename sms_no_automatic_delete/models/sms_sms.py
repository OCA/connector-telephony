# Copyright 2021 Akretion (https://www.akretion.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

from odoo import api, models
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class SmsSms(models.Model):
    _inherit = "sms.sms"

    @api.model
    def _purge(self, days):

        purge_day = datetime.now() - timedelta(days=days)
        purge_day = purge_day.strftime(DEFAULT_SERVER_DATE_FORMAT)
        sms = self.env["sms.sms"].search([("write_date", "<=", purge_day)])
        sms.with_context(force_unlink=True).unlink()

    def unlink(self):
        if self._context.get("force_unlink"):
            return super().unlink()
        else:
            return True
