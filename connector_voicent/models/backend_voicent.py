# Copyright (C) 2019 Open Source Integrators
# <https://www.opensourceintegrators.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from pytz import timezone
from odoo.addons.connector_voicent.examples import voicent


class BackendVoicent(models.Model):
    _name = 'backend.voicent'
    _description = 'Voicent Backend'
    _inherit = ['connector.backend']
    _rec_name = 'host'

    host = fields.Char(
        string='Host',
        required=True,
    )
    port = fields.Integer(
        string='Port',
        required=True,
    )
    next_call = fields.Datetime(
        string='Next Call',
        copy=False,
    )
    call_line_ids = fields.One2many(
        string='Call Lines',
        comodel_name='backend.voicent.call.line',
        inverse_name='backend_id',
    )
    time_line_ids = fields.One2many(
        string='Call Times',
        comodel_name='backend.voicent.time.line',
        inverse_name='backend_id',
    )

    @api.model
    def _run_check_the_voicent_status(self):
        ''' This method is called from a cron job. '''
        backend_voicent_rec = self.search([])
        current_dt = datetime.datetime.now()
        status = False
        queue_job = self.env['queue.job']
        user_tz = timezone(
            self.env.context.get('tz') or self.env.user.tz or 'UTC')
        dt_value = current_dt.astimezone(user_tz)
        convt_dt_strf = dt_value.strftime(
            DEFAULT_SERVER_DATETIME_FORMAT)
        convt_dt = datetime.datetime.strptime(
            convt_dt_strf,
            DEFAULT_SERVER_DATETIME_FORMAT)
        current_time = convt_dt.strftime("%H:%M")
        for time_line_rec in backend_voicent_rec.time_line_ids:
            hours, minutes = divmod(abs(time_line_rec.time) * 60, 60)
            minutes = round(minutes)
            if minutes == 60:
                minutes = 0
                hours += 1
            line_time = '%02d:%02d' % (hours, minutes)
            if current_time == line_time:
                backend_voicent_rec.next_call = datetime.datetime.now()
                queue_rec = queue_job.search([('state', '=',
                                               'waiting_voicent_status')])
                for q_rec in queue_rec:
                    v = voicent.Voicent()
                    status = v.checkStatus(q_rec.voicent_campaign)
        return status


class BackendVoicentTimeLine(models.Model):
    _name = 'backend.voicent.time.line'
    _description = 'Voicent Backend Time Line'

    name = fields.Char(
        string='Name',
        required=True,
    )
    time = fields.Float(
        string='Time',
        copy=False,
    )
    backend_id = fields.Many2one(
        string='Backend',
        comodel_name='backend.voicent',
        ondelete='set null',
    )


class BackendVoicentCallLine(models.Model):
    _name = 'backend.voicent.call.line'
    _description = 'Voicent Backend Call Line'

    name = fields.Char(
        string='Name',
        required=True,
    )
    applies_on = fields.Selection(
        string='Applies on',
        selection=[],
    )
    voicent_app = fields.Char(
        string='Voicent App',
    )
    backend_id = fields.Many2one(
        string='Backend',
        comodel_name='backend.voicent',
        ondelete='set null',
    )
