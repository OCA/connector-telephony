# Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
# Copyright (C) 2013 Julius Network Solutions SARL <contact@julius.fr>
# Copyright (C) 2015 Valentin Chemiere <valentin.chemiere@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class ServerAction(models.Model):
    """
    Possibility to specify the SMS Gateway when configure this server action
    """
    _inherit = 'ir.actions.server'

    mobile = fields.Char(
        string='Mobile No',
        help="Field to be used to fetch the mobile number, e.g. you select"
             " the invoice model and `object.invoice_address_id.mobile` "
             "will be the field providing the correct mobile number.")
    sms = fields.Char(string='SMS', size=160, translate=True)
    sms_server_id = fields.Many2one(
        comodel_name='sms.gateway', string='SMS Server',
        help='Select the SMS Gateway configuration to use with this action.')
    sms_template_id = fields.Many2one(
        comodel_name='mail.template', string='SMS Template',
        help='Select the SMS Template configuration to use with this action.')
