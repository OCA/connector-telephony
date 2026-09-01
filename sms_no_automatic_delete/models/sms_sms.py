# Copyright 2021 Akretion (https://www.akretion.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
from datetime import datetime, timedelta

from odoo import api, models
from odoo.tools.sql import SQL

_logger = logging.getLogger(__name__)


class SmsSms(models.Model):
    _inherit = "sms.sms"

    IAP_TO_SMS_STATE_SUCCESS = {
        "processing": "process",
        "success": "sent",
        "sent": "sent",
        "delivered": "sent",
    }

    @api.autovacuum
    def _gc_device(self):
        sms_purge_days = int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("sms_no_automatic_delete.sms_purge_days", 90)
        )

        purge_date = datetime.now() - timedelta(days=sms_purge_days)

        self.env.cr.execute(
            SQL(
                """
            DELETE FROM sms_sms
            WHERE to_delete = TRUE AND write_date <= %(purge_date)s
            """,
                purge_date=purge_date,
            )
        )

        _logger.info("GC'd %d sms marked for deletion", self._cr.rowcount)
