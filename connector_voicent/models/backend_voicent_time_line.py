# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class BackendVoicentTimeLine(models.Model):
    _name = 'backend.voicent.time.line'
    _description = 'Voicent Backend Time Line'

    name = fields.Char(
        string=u'Name',
        required=True,
    )
    time = fields.Datetime(
        string=u'Time',
        copy=False,
        default=lambda self: fields.Datetime.now(),
    )
    backend_id = fields.Many2one(
        string=u'Backend',
        comodel_name='backend.voicent',
        ondelete='set null',
    )
