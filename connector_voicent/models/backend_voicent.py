# Copyright (C) 2019 Open Source Integrators
# <https://www.opensourceintegrators.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields, models
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from pytz import timezone
from ..examples import voicent


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
    is_active = fields.Boolean('Is Active')

    @api.model
    def _run_check_the_voicent_status(self):
        ''' This method is called from a cron job. '''

        cr_time_list = []
        is_next_day = False
        backend_voicent_rec = self.search([('is_active', '=', True)])
        for backend_voicent in backend_voicent_rec:
            current_dt = datetime.now(timezone('UTC'))
            user_tz = timezone(
                self.env.context.get('tz') or self.env.user.tz or 'UTC')
            dt_value = current_dt.astimezone(user_tz)
            convt_dt_strf = dt_value.strftime(
                DEFAULT_SERVER_DATETIME_FORMAT)
            convt_dt = datetime.strptime(
                convt_dt_strf,
                DEFAULT_SERVER_DATETIME_FORMAT)
            current_time = convt_dt.strftime("%H:%M")
            for time_line_rec in backend_voicent.time_line_ids:
                hours, minutes = divmod(abs(time_line_rec.time) * 60, 60)
                minutes = round(minutes)
                if minutes == 60:
                    minutes = 0
                    hours += 1
                line_time = '%02d:%02d' % (hours, minutes)
                cr_time_list.append(line_time)
            cr_time_list = sorted(cr_time_list)
            next_call = datetime.now()
            for each_time_entry in cr_time_list:
                if each_time_entry > current_time and not is_next_day:
                    next_call = datetime.now().replace(
                        hour=int(each_time_entry.split(':')[0]),
                        minute=int(each_time_entry.split(':')[1]))
                    is_next_day = True
            if cr_time_list and not is_next_day:
                next_call = datetime.now().replace(
                    hour=int(cr_time_list[0].split(':')[0]),
                    minute=int(cr_time_list[0].split(':')[1])) + timedelta(
                    days=1)
            next_call_tz = timezone(self.env.context.get(
                'tz') or self.env.user.tz).localize(next_call, is_dst=False)
            next_call_utc = next_call_tz.astimezone(timezone('UTC'))
            next_call_utc = datetime.strptime(
                fields.Datetime.to_string(next_call_utc),
                DEFAULT_SERVER_DATETIME_FORMAT)
            backend_voicent.next_call = fields.Datetime.to_string(
                next_call_utc)


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
