# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class VoipCall(models.Model):
    _inherit = "voip.call"

    transcript = fields.Text()
    transcript_state = fields.Selection(
        [("pending", "Pending"), ("done", "Done")],
        compute="_compute_transcript_state",
        store=True,
    )

    @api.depends("transcript", "recording_filename", "pbx_id.transcribe_call_records")
    def _compute_transcript_state(self):
        """Inherit this method to compute the transcript state"""
        for rec in self:
            transcript_state = ""
            if rec.pbx_id.transcribe_call_records and rec.recording_filename:
                transcript_state = rec.transcript and "done" or "pending"
            rec.transcript_state = transcript_state

    def transcribe_calls(self):
        pbxs = self.mapped("pbx_id")
        for pbx in pbxs:
            calls = self.filtered(lambda c, pbx_rec=pbx: c.pbx_id == pbx_rec)
            self.env.cr.execute(
                """SELECT id
                   FROM voip_call
                   WHERE transcript IS NULL
                   AND id in %s
                   AND recording_filename IS NOT NULL
                   FOR UPDATE NOWAIT""",
                (tuple(calls.ids),),
                log_exceptions=False,
            )
            call_ids = [aml_id for (aml_id,) in self.env.cr.fetchall()]
            calls = self.env["voip.call"].browse(call_ids)
            pbx._transcribe_calls(calls)
