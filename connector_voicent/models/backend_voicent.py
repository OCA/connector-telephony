# Copyright (C) 2021 Open Source Integrators
# <https://www.opensourceintegrators.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from datetime import datetime, timedelta

from pytz import timezone

from odoo import api, fields, models
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class BackendVoicent(models.Model):
    _name = "backend.voicent"
    _description = "Voicent Backend"
    _inherit = ["connector.backend"]

    name = fields.Char(string="Name", required=True)
    host = fields.Char(string="Host", default="localhost", required=True)
    port = fields.Integer(string="Port", default="8155", required=True)
    callerid = fields.Char(string="Caller ID", required=True)
    line = fields.Integer(string="Number of lines", required=True)
    next_call = fields.Datetime(string="Next Call", copy=False)
    call_line_ids = fields.One2many(
        string="Call Lines",
        comodel_name="backend.voicent.call.line",
        inverse_name="backend_id",
    )
    time_line_ids = fields.One2many(
        string="Call Times",
        comodel_name="backend.voicent.time.line",
        inverse_name="backend_id",
    )
    active = fields.Boolean("Active", default=True)

    @api.model
    def _run_update_next_call(self):
        """ This method is called from a cron job. """
        cr_time_list = ["00:00"]
        backends = self.search([("active", "=", True)])
        for backend in backends:
            user_tz = timezone(self.env.context.get("tz") or self.env.user.tz or "UTC")
            current_time = datetime.now(user_tz).strftime("%H:%M")
            for time_line_rec in backend.time_line_ids:
                hours, minutes = divmod(abs(time_line_rec.time) * 60, 60)
                minutes = round(minutes)
                if minutes == 60:
                    minutes = 0
                    hours += 1
                line_time = "%02d:%02d" % (hours, minutes)
                cr_time_list.append(line_time)
            cr_time_list = sorted(cr_time_list)
            next_call = False
            for time_entry in cr_time_list:
                if time_entry > current_time:
                    next_call = datetime.now(user_tz).replace(
                        hour=int(time_entry.split(":")[0]),
                        minute=int(time_entry.split(":")[1]),
                        second=0,
                    )
                    break
            if not next_call:
                next_call = (
                    datetime.now(user_tz).replace(
                        hour=int(cr_time_list[0].split(":")[0]),
                        minute=int(cr_time_list[0].split(":")[1]),
                        second=0,
                    )
                    + timedelta(days=1)
                )
            next_call = next_call.astimezone(timezone("UTC"))
            backend.next_call = next_call.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
