# Copyright 2025 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.AbstractModel):
    _inherit = "mail.activity.mixin"

    activity_main_partner_id = fields.Many2one(
        "res.partner",
        string="Main Contact",
        compute="_compute_activity_main_partner_id",
    )

    def _compute_activity_main_partner_id(self):
        for record in self:
            record.activity_main_partner_id = record.get_activity_main_partner_id()

    def get_activity_main_partner_id(self):
        if "partner_id" in self._fields:
            return self.partner_id
        return self.env["res.partner"]
