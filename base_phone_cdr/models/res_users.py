from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    related_phone = fields.Char("Related Phone")
    phone_password = fields.Char("Phone Password")
