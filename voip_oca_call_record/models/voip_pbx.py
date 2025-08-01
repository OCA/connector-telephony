# Copyright 2025 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class VoipOcaPbx(models.Model):
    _inherit = "voip.pbx"

    call_record_mode = fields.Selection(
        [
            ("manual", "Manual"),
            ("auto", "Automatic"),
            ("sample", "Sampled"),
        ]
    )

    call_recording_sample_rate = fields.Float("Default Sample Rate (%)", default=10.0)
