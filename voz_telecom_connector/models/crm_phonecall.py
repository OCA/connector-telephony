# © 2022 CONINPE Consultores Informaticos: Telmo Suarez Venero <tsuarez@zertek.es>
# License AGPL-3.0 or later (http://gnu.org/license/agpl.html).
from odoo import fields, models


class CrmPhonecall(models.Model):
    _inherit = "crm.phonecall"

    voz_telecom_call_id = fields.Char(string="Id de llamada de VozTelecom")
    voz_telecom_state = fields.Char(string="Estado de VozTelecom")
    end_date = fields.Datetime(string="Call end date")
    duration = fields.Float(compute="_compute_duration")

    _sql_constraints = [
        (
            "voz_telecom_call_id_unique",
            "unique(voz_telecom_call_id)",
            "No pueden existir dos llamadas con el mismo id",
        )
    ]

    def _compute_duration(self):
        for record in self:
            if record.end_date:
                record.duration = (record.end_date - record.date).total_seconds() / 60
            else:
                record.duration = 0.0

    def api_drop_call(self):
        api_controller = self.env["voztelecom.config"].search([])[0]
        api_controller.api_drop_call(self.voz_telecom_call_id)
