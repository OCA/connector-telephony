# Copyright 2012-2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class ResUsers(models.Model):
    _inherit = "res.users"

    # Field name starts with 'context_' to allow modification by the user
    # in his preferences, cf odoo/odoo/addons/base/res/res_users.py
    # in "def write()" of "class Users(models.Model)"
    context_propose_creation_crm_call = fields.Boolean(
        string='Propose to create a call in CRM after a click2dial',
        default=True)
