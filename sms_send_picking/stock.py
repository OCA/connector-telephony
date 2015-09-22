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

    availability_sent_by_sms = fields.Boolean(default=False)

    #TODO use a templating instead
    @api.model
    def _prepare_availability_sms_notification(self):
        gateway = self.env['sms.gateway'].search([
            ('default_gateway', '=', True)], limit=1)
        return {
            'gateway_id': gateway.id,
            'message': _('Your picking %s is ready to transfert') % self.name,
            'mobile': self.partner_id.mobile,
            'partner_id': self.partner_id.id,
            'state': 'draft',
            'validity': gateway.validity,
            'classes': gateway.classes,
            'deferred': gateway.deferred,
            'priority': gateway.priority,
            'coding': gateway.coding,
            'nostop': gateway.nostop,
            'company_id': self.company_id.id,
        }

    @api.model
    def _get_send_picking_availability_sms_domain(self):
        return [
            ('state', '=', 'assigned'),
            ('availability_sent_by_sms', '=', False),
            ('picking_type_id.code', '=', 'outgoing'),
            ]

    @api.model
    def _cron_send_picking_availability_by_sms(self):
        domain = self._get_send_picking_availability_sms_domain()
        pickings = self.env['stock.picking'].search(domain)
        for picking in pickings:
            vals = picking._prepare_availability_sms_notification()
            self.env['sms.sms'].create(vals)
        pickings.write({'availability_sent_by_sms': True})
