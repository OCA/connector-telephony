# Copyright 2026 Akretion (https://www.akretion.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    sms_purge_days = fields.Integer(
        string="SMS Purge Days",
        default=90,
        config_parameter="sms_no_automatic_delete.sms_purge_days",
    )
