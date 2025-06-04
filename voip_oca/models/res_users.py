# Copyright 2025 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    voip_pbx_id = fields.Many2one("voip.pbx")
    voip_username = fields.Char()
    voip_password = fields.Char()

    @property
    def SELF_READABLE_FIELDS(self):
        return super().SELF_READABLE_FIELDS + [
            "voip_pbx_id",
            "voip_username",
            "voip_password",
        ]

    @property
    def SELF_WRITEABLE_FIELDS(self):
        return super().SELF_WRITEABLE_FIELDS + [
            "voip_pbx_id",
            "voip_username",
            "voip_password",
        ]

    def _voip_get_info(self):
        return {
            "pbx_id": self.voip_pbx_id.id,
            "pbx": self.voip_pbx_id.name,
            "pbx_domain": self.voip_pbx_id.domain,
            "pbx_ws": self.voip_pbx_id.ws_server,
            "mode": (
                self.voip_username and self.voip_password and self.voip_pbx_id.mode
            )
            or "test",
            "pbx_username": self.voip_username,
            "pbx_password": self.voip_password,
            "tones": {
                "dialtone": "/voip_oca/static/audio/dialtone.mp3",
                "calltone": "/voip_oca/static/audio/calltone.mp3",
                "ringbacktone": "/voip_oca/static/audio/ringbacktone.mp3",
            },
        }
