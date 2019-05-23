# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class BackendVoicent(models.Model):
    _name = 'backend.voicent'
    _description = 'Voicent Backend'
    _rec_name = 'host'

    host = fields.Char(
        string=u'Host',
        required=True,
    )
    port = fields.Integer(
        string=u'Port',
        required=True,
    )
    next_call = fields.Datetime(
        string=u'Next Call',
        copy=False,
        default=lambda self: fields.Datetime.now(),
    )
    call_line_ids = fields.One2many(
        string=u'Call Lines',
        comodel_name='backend.voicent.call.line',
        inverse_name='backend_id',
    )
    time_line_ids = fields.One2many(
        string=u'Call Times',
        comodel_name='backend.voicent.time.line',
        inverse_name='backend_id',
    )
