# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2013 Julius Network Solutions SARL <contact@julius.fr>
#    Copyright (C) 2015 Valentin Chemiere <valentin.chemiere@akretion.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api
import time
import logging
import urllib

_logger = logging.getLogger('gateway')


class ServerAction(models.Model):
    """
    Possibility to specify the SMS Gateway when configure this server action
    """
    _inherit = 'ir.actions.server'

    mobile = fields.Char('Mobile No', help="Field to be "
                         "be used to fetch the mobile number, e.g. you select"
                         " the invoice model and "
                         "`object.invoice_address_id.mobile` will be the "
                         "field providing the correct mobile number.")
    sms = fields.Char('SMS', size=160, translate=True)
    sms_server = fields.Many2one('sms.gateway', 'SMS Server',
                                 help='Select the SMS Gateway configuration'
                                 ' to use with this action.')
    sms_template_id = fields.Many2one('email.template', 'SMS Template',
                                      help='Select the SMS Template'
                                      ' configuration to use with this action.')

