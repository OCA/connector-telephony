# Copyright 2025 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import api, fields, models
from odoo.osv import expression


class VoipOcaCall(models.Model):
    _name = "voip.call"
    _description = "Voip OCA Call"

    phone_number = fields.Char(required=True)
    type_call = fields.Selection(
        [
            ("incoming", "Incoming"),
            ("outgoing", "Outgoing"),
        ],
        default="outgoing",
    )
    state = fields.Selection(
        [
            ("aborted", "Aborted"),
            ("calling", "Calling"),
            ("missed", "Missed"),
            ("ongoing", "Ongoing"),
            ("rejected", "Rejected"),
            ("terminated", "Terminated"),
        ],
        default="calling",
        index=True,
    )
    pbx_id = fields.Many2one("voip.pbx", "PBX")
    end_date = fields.Datetime()
    start_date = fields.Datetime()
    activity_name = fields.Char(
        help="The name of the activity related to this phone call, if any."
    )
    partner_id = fields.Many2one("res.partner", "Contact", index=True)
    user_id = fields.Many2one(
        "res.users", "Responsible", default=lambda self: self.env.uid, index=True
    )

    @api.depends("state", "partner_id.name")
    def _compute_display_name(self):
        states = dict(self._fields["state"].selection)
        for rec in self:
            name = rec.partner_id.display_name or rec.phone_number
            rec.display_name = f"{states[rec.state]} - {name}"

    def format_call(self):
        return {
            "id": self.id,
            "creationDate": self.create_date,
            "typeCall": self.type_call,
            "displayName": self.display_name,
            "endDate": self.end_date,
            "partner": self.partner_id and self.partner_id.format_partner(),
            "phoneNumber": self.phone_number,
            "startDate": self.start_date,
            "createDate": self.create_date,
            "state": self.state,
        }

    @api.model
    def get_recent_calls(self, _search, offset, limit):
        domain = [("user_id", "=", self.env.uid)]
        if _search:
            search_fields = [
                "phone_number",
                "partner_id.name",
                "activity_name",
            ]
            search_domain = expression.OR(
                [[(field, "ilike", _search)] for field in search_fields]
            )
            domain = expression.AND([domain, search_domain])
        return [
            call.format_call()
            for call in self.search(
                domain, offset=offset, limit=limit, order="create_date DESC"
            )
        ]

    @api.model
    def create_call(self, values):
        if not values.get("partner_id"):
            values["partner_id"] = (
                self.env["res.partner"]
                .search(
                    [
                        "|",
                        ("phone", "=", values.get("phone_number")),
                        ("mobile", "=", values.get("phone_number")),
                    ],
                    limit=1,
                )
                .id
            )
        return self.create(values).format_call()

    def terminate_call(self):
        self.end_date = fields.Datetime.now()
        self.state = "terminated"
        return self.format_call()

    def reject_call(self):
        self.end_date = fields.Datetime.now()
        self.state = "rejected"
        return self.format_call()

    def accept_call(self):
        self.start_date = fields.Datetime.now()
        self.state = "ongoing"
        return self.format_call()
