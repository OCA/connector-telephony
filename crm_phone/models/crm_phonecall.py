# Copyright 2012-2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class CrmPhonecall(models.Model):
    _name = "crm.phonecall"
    _description = "Phone Call"
    _inherit = ["mail.thread", "mail.activity.mixin", "phone.validation.mixin"]
    _order = "id desc"

    # Restore the object that existed in v8
    # and doesn't exist in v9 community any more
    name = fields.Char(string="Call Summary", required=True, tracking=True)
    date = fields.Datetime(
        string="Date",
        tracking=True,
        copy=False,
        default=lambda self: fields.Datetime.now(),
    )
    description = fields.Text(string="Description", copy=False)
    company_id = fields.Many2one(
        "res.company", string="Company", default=lambda self: self.env.company
    )
    user_id = fields.Many2one(
        "res.users",
        string="Responsible",
        tracking=True,
        default=lambda self: self.env.user,
    )
    team_id = fields.Many2one(
        "crm.team",
        string="Sales Team",
        tracking=True,
        default=lambda self: self.env["crm.team"]
        .sudo()
        ._get_default_team_id(user_id=self.env.uid),
    )
    partner_id = fields.Many2one("res.partner", string="Contact", ondelete="cascade")
    partner_phone = fields.Char(string="Phone")
    partner_mobile = fields.Char(string="Mobile")
    priority = fields.Selection(
        [("0", "Low"), ("1", "Normal"), ("2", "High")],
        string="Priority",
        tracking=True,
        default="1",
    )
    opportunity_id = fields.Many2one(
        "crm.lead", string="Lead/Opportunity", ondelete="cascade", tracking=True
    )
    state = fields.Selection(
        [
            ("open", "To Do"),
            ("done", "Held"),
            ("cancel", "Cancelled"),
        ],
        string="Status",
        default="open",
        copy=False,
        required=True,
        tracking=True,
        help="The status is set to Confirmed, when a case is created.\n"
        "When the call is over, the status is set to Held.\n"
        "If the call is not applicable anymore, the status can be set to "
        "Cancelled.",
    )
    direction = fields.Selection(
        [
            ("inbound", "Inbound"),
            ("outbound", "Outbound"),
        ],
        string="Type",
        required=True,
        default="outbound",
    )

    @api.onchange("partner_id")
    def onchange_partner_id(self):
        if self.partner_id:
            self.partner_phone = self.partner_id.phone
            self.partner_mobile = self.partner_id.mobile

    @api.onchange("opportunity_id")
    def onchange_opportunity_id(self):
        if self.opportunity_id:
            self.partner_phone = self.opportunity_id.phone
            self.partner_mobile = self.opportunity_id.mobile
            self.team_id = self.opportunity_id.team_id.id
            self.partner_id = self.opportunity_id.partner_id.id

    @api.onchange("partner_phone")
    def onchange_partner_phone(self):
        if self.partner_phone:
            self.partner_phone = self.phone_format(self.partner_phone)

    @api.onchange("partner_mobile")
    def onchange_partner_mobile(self):
        if self.partner_mobile:
            self.partner_mobile = self.phone_format(self.partner_mobile)

    def schedule_another_call(self):
        self.ensure_one()
        ctx = self._context.copy()
        ctx.update(
            {
                "default_date": False,
                "default_partner_id": self.partner_id.id,
                "default_opportunity_id": self.opportunity_id.id,
                "default_direction": "outbound",
                "default_partner_phone": self.partner_phone,
                "default_partner_mobile": self.partner_mobile,
            }
        )
        action = self.env.ref("crm_phone.crm_phonecall_action").sudo().read()[0]
        action.update(
            {
                "view_mode": "form,tree,calendar",
                "views": False,
                "context": ctx,
            }
        )
        return action
