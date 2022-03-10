# Copyright 2012-2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    phonecall_ids = fields.One2many("crm.phonecall", "partner_id", string="Phone Calls")
    phonecall_count = fields.Integer(
        compute="_compute_phonecall_count", string="Number of Phonecalls"
    )

    @api.depends("phonecall_ids")
    def _compute_phonecall_count(self):
        for partner in self:
            partner.phonecall_count = self.env["crm.phonecall"].search_count(
                [
                    ("partner_id", "child_of", partner.id),
                ]
            )
