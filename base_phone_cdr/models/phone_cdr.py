# Copyright (C) 2024 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class PhoneCDR(models.Model):
    _name = "phone.cdr"
    _description = "Phone CDR"

    @api.depends("call_start_time", "call_connect_time", "inbound_flag")
    def _compute_ring_time(self):
        for rec in self:
            ring_time = 0.0
            if rec.inbound_flag and rec.call_connect_time and rec.call_start_time:
                duration = rec.call_connect_time - rec.call_start_time
                ring_time = divmod(duration.total_seconds(), 3600)[0]
            rec.ring_time = ring_time

    @api.depends("called_id", "inbound_flag")
    def _compute_odoo_user(self):
        for rec in self:
            user_id = False
            if rec.inbound_flag:
                user_id = (
                    self.env["res.users"]
                    .search(
                        [
                            ("related_phone", "=", rec.called_id),
                            ("related_phone", "!=", False),
                        ],
                        limit=1,
                    )
                    .id
                )
            rec.user_id = user_id

    guid = fields.Char("Call GUID")
    inbound_flag = fields.Selection(
        [("outbound", "Outbound"), ("inbound", "Inbound")], string="Call Inbound flag"
    )
    call_start_time = fields.Datetime("Call start time")
    call_connect_time = fields.Datetime("Call connect time")
    ring_time = fields.Float(compute="_compute_ring_time", string="Compute ring time")
    talk_time = fields.Datetime("Talk Time")
    caller_id = fields.Char("Caller ID")
    caller_id_name = fields.Char("Caller ID Name")
    called_id = fields.Char("Called ID")
    called_id_name = fields.Char("Called ID Name")
    state = fields.Selection(
        [
            ("offering", "Offering"),
            ("connected", "Connected"),
            ("missed", "Missed"),
            ("on_hold", "On Hold"),
            ("completed", "Completed"),
        ],
        string="Status",
        default="offering",
    )
    user_id = fields.Many2one(
        "res.users", compute="_compute_odoo_user", string="Odoo User"
    )
    partner_id = fields.Many2one("res.partner", string="Partner")

    @api.model_create_multi
    def create(self, vals_list):
        phonc_cdr_rec = super().create(vals_list)
        for rec in phonc_cdr_rec:
            if rec.inbound_flag:
                rec.partner_id = self.env["res.partner"].search(
                    [("phone", "=", rec.called_id), ("phone", "!=", False)], limit=1
                )
        return phonc_cdr_rec

    def write(self, vals):
        res = super().write(vals)
        if vals.get("inbound_flag") or vals.get("called_id"):
            for rec in self:
                rec.partner_id = self.env["res.partner"].search(
                    [("phone", "=", rec.called_id), ("phone", "!=", False)], limit=1
                )
        return res
