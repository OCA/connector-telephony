# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    can_call = fields.Boolean(
        string=u'Accepts Calls',
    )
