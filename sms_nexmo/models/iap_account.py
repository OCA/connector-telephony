# Copyright 2020 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class IapAccount(models.Model):

    _inherit = 'iap.account'

    key = fields.Char()
    secret = fields.Char()
