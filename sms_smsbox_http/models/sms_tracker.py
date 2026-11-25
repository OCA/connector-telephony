# Copyright 2026 INVITU (<https://www.invitu.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models

SMSBOX_DELIVERED = {"0"}
SMSBOX_PENDING = {"9", "10"}
SMSBOX_DELIVERY_ERRORS = {
    "-3": "not_delivered",
    "-1": "not_delivered",
    "1": "not_delivered",
    "2": "rejected",
    "3": "expired",
    "4": "not_delivered",
    "5": "not_delivered",
    "6": "not_delivered",
    "7": "invalid_destination",
    "8": "not_allowed",
}


class SmsTracker(models.Model):
    _inherit = "sms.tracker"

    sms_smsbox_http_reference = fields.Char(string="SMSBOX Reference", readonly=True)

    def _action_update_from_smsbox_http(self, accuse):
        """Update notifications from a SMSBOX delivery report status code."""
        if accuse in SMSBOX_DELIVERED:
            self._action_update_from_sms_state("sent")
        elif accuse in SMSBOX_PENDING:
            self._action_update_from_sms_state("pending")
        elif accuse in SMSBOX_DELIVERY_ERRORS:
            self._action_update_from_provider_error(SMSBOX_DELIVERY_ERRORS[accuse])
