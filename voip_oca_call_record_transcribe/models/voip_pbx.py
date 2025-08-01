# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class VoipOcaPbx(models.Model):
    _inherit = "voip.pbx"

    transcribe_call_records = fields.Boolean()

    def _get_transcribe_pbx_domain(self):
        return [("transcribe_call_records", "=", True)]

    def cron_transcribe_call(self):
        pbxs = self.search(self._get_transcribe_pbx_domain())
        for pbx in pbxs:
            pbx.transcribe_calls()

    def _transcribe_calls(self, calls):
        """Inherit to implement the actual transcription logic"""
        raise NotImplementedError()

    def _get_calls_to_transcribe(self):
        # Lock the call records being transcribed
        self.env.cr.execute(
            """SELECT id
               FROM voip_call
               WHERE transcript IS NULL
               AND pbx_id = %s
               AND recording_filename IS NOT NULL
               FOR UPDATE NOWAIT""",
            (self.id,),
            log_exceptions=False,
        )
        call_ids = [aml_id for (aml_id,) in self.env.cr.fetchall()]
        calls = self.env["voip.call"].browse(call_ids)
        return calls

    def transcribe_calls(self):
        self.ensure_one()
        calls = self._get_calls_to_transcribe()
        self._transcribe_calls(calls)
