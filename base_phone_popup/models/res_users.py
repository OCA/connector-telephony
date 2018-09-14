# Copyright 2014-2016 Akretion, Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    context_incall_popup = fields.Boolean(
        string='Pop-up on Incoming Calls',
        default=True,
    )
