# Copyright 2025 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import AccessError
from odoo.osv import expression


class VoipOcaActivity(models.Model):
    _inherit = "mail.activity"

    main_partner_id = fields.Many2one(
        "res.partner", string="Main Contact", compute="_compute_main_partner_id"
    )
    main_partner = fields.Char(compute="_compute_main_partner_id")

    @api.depends("res_id")
    def _compute_main_partner_id(self):
        for activity in self:
            partner = (
                self.env[activity.res_model]
                .browse(activity.res_id)
                .activity_main_partner_id
            )
            activity.main_partner_id = partner
            activity.main_partner = partner.name

    @api.model
    def get_call_activities(self, _search, offset, limit):
        activity_type_id = self.env["mail.activity.type"].search(
            [("category", "=", "phonecall")]
        )
        domain = [
            ("user_id", "=", self.env.uid),
            ("activity_type_id", "in", activity_type_id.ids),
            ("date_deadline", "<=", fields.Datetime.now()),
        ]
        if _search:
            search_fields = ["res_name", "summary", "date_deadline"]
            search_domain = expression.OR(
                [[(field, "ilike", _search)] for field in search_fields]
            )
            domain = expression.AND([domain, search_domain])
        all_activities = self.search(domain, offset=offset, limit=limit)
        # Filter activities to avoid accessing records that the user cannot read
        # due to multi-company restrictions or other access rules in the res_model.
        no_access_ids = []
        for activity in all_activities:
            try:
                res_record = self.env[activity.res_model].browse(activity.res_id)
                res_record.check_access_rule("read")
            except AccessError:
                no_access_ids.append(activity.id)
        if no_access_ids:
            all_activities -= self.browse(no_access_ids)
        return all_activities.activity_format()
