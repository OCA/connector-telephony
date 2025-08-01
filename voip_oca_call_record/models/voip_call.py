# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class VoipCall(models.Model):
    _inherit = "voip.call"

    recording = fields.Binary(
        "Call Recording", attachment=True, help="Base64 encoded call recording data"
    )
    recording_filename = fields.Char()

    def _get_recording_filename(self):
        return (
            f"call_{self.id}_to_{self.phone_number}"
            f"_recording_{self.create_date.date()}.webm"
        )

    @api.model
    def save_call_recording(self, call_id, recording_data):
        """Save the call recording sent from JS as base64"""
        call = self.browse(call_id)
        filename = call._get_recording_filename()
        if call.exists():
            # remove the data URL prefix if present
            if recording_data.startswith("data:"):
                recording_data = recording_data.split(",", 1)[1]
            call.write(
                {
                    "recording": recording_data,
                    "recording_filename": filename,
                }
            )
        return True
