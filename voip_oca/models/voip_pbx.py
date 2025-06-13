# Copyright 2025 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class VoipOcaPbx(models.Model):
    _name = "voip.pbx"
    _description = "Voip Pbx"

    name = fields.Char(required=True)
    domain = fields.Char(default="localhost")
    ws_server = fields.Char(default="ws://localhost")
    mode = fields.Selection(
        [("test", "Test"), ("prod", "Production")],
        string="Environment",
        default="test",
    )
