from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    external_code = fields.Char("External Code")
