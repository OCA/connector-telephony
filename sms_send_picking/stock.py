# -*- coding: utf-8 -*-
###############################################################################
#
#   Module for Odoo
#   Copyright (C) 2015 Akretion (http://www.akretion.com).
#   @author Valentin CHEMIERE <valentin.chemiere@akretion.com>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from openerp import api, models, fields
from openerp.tools.translate import _


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    sms_sent = fields.Boolean(default=False)

    @api.model
    def _send_sms(self):
        sms_sender_obj = self.env['partner.sms.send']
        gateways = self.env['sms.smsclient'].search([('default_gateway', '=',
                                                      True)], limit=1)
        gateway = gateways[0]
        pickings = self.env['stock.picking'].search(
            [('state', '=', 'assigned'), ('sms_sent', '=', False),
             ('picking_type_id.code', '=', 'outgoing')])
        for pick in pickings:
            data = {
                'gateway': gateway.id,
                'text': _('Your picking %s is ready to transfert') % pick.name,
                'mobile_to': pick.partner_id.phone,
            }
            sms_sender = sms_sender_obj.create(data)
            sms_sender.sms_send()
            pick.sms_sent = True
