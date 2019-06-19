# Copyright (C) 2019 Open Source Integrators
# <https://www.opensourceintegrators.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class BackendVoicentTimeLine(models.Model):
    _name = 'backend.voicent.time.line'
    _description = 'Voicent Backend Time Line'
    _order = 'time'

    name = fields.Char(string='Name', required=True)
    time = fields.Float(string='Time', copy=False)
    backend_id = fields.Many2one(
        string='Backend',
        comodel_name='backend.voicent',
        ondelete='set null')
