from ast import literal_eval

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    total_cdr_count = fields.Integer(
        compute="_compute_total_cdr_count", string="Total CDR"
    )

    def _compute_total_cdr_count(self):
        for partner in self:
            cdr_records = self.env["phone.cdr"].search(
                [("partner_id", "=", partner.id)]
            )
            partner.total_cdr_count = cdr_records and len(cdr_records) or 0

    @api.multi
    def action_view_partner_cdr_records(self):
        self.ensure_one()
        action = self.env.ref("base_phone_cdr.phone_cdr_view_action").read()[0]
        action["domain"] = literal_eval(action["domain"])
        action["domain"].append(("partner_id", "=", self.id))
        return action
