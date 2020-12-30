# -*- coding: utf-8 -*-

from odoo import models, fields


class ResUsers(models.Model):
    _inherit = 'res.users'

    related_phone = fields.Char('Related Phone')
    phone_password = fields.Char('Phone Password')