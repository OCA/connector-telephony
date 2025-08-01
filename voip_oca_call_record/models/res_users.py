# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    call_record_mode = fields.Selection(
        [
            ("manual", "Manual"),
            ("auto", "Automatic"),
            ("sample", "Sampled"),
        ]
    )

    def _voip_get_info(self):
        data = super()._voip_get_info()
        data["call_record_mode"] = self.voip_pbx_id.call_record_mode
        if self.call_record_mode:
            data["call_record_mode"] = self.call_record_mode
        data["call_recording_sample_rate"] = self.voip_pbx_id.call_recording_sample_rate
        return data
