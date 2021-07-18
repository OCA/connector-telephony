# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class IapAccount(models.Model):

    _inherit = "iap.account"

    key = fields.Char()
