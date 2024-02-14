# Copyright (C) 2024 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from ast import literal_eval

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    total_cdr_count = fields.Integer(
        compute="_compute_total_cdr_count", string="Total CDR"
    )

    def _compute_total_cdr_count(self):
        for partner in self:
            cdr_records_count = self.env["phone.cdr"].search_count(
                [("partner_id", "=", partner.id)]
            )
            partner.total_cdr_count = cdr_records_count

    def action_view_partner_cdr_records(self):
        self.ensure_one()
        action = self.env.ref("base_phone_cdr.phone_cdr_view_action").read()[0]
        action["domain"] = literal_eval(action["domain"])
        action["domain"].append(("partner_id", "=", self.id))
        return action
