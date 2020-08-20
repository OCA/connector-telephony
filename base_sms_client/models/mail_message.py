# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MailMessage(models.Model):

    _inherit = 'mail.message'

    message_type = fields.Selection(selection_add=[('sms', 'SMS')])
