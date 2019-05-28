# Copyright (C) 2019 Open Source Integrators
# <https://www.opensourceintegrators.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


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
        default=lambda self: fields.Datetime.now(),
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
