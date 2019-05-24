# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class BackendVoicentCallLine(models.Model):
    _name = 'backend.voicent.call.line'
    _description = 'Voicent Backend Call Line'

    name = fields.Char(
        string=u'Name',
        required=True,
    )
    applies_on = fields.Selection(
        string=u'Applies on',
        selection=[],
    )
    voicent_app = fields.Char(
        string=u'Voicent App',
    )
    backend_id = fields.Many2one(
        string=u'Backend',
        comodel_name='backend.voicent',
        ondelete='set null',
    )
