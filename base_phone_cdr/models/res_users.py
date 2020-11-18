# -*- coding: utf-8 -*-

from odoo import api, models, fields, _


class ResUsers(models.Model):
    _inherit = 'res.users'

    related_phone = fields.Char('Related Phone')