# -*- coding: utf-8 -*-
# © 2015 Valentin CHEMIERE <valentin.chemiere@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models, fields
from odoo.tools.translate import _
import logging

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    availability_sent_by_sms = fields.Boolean(default=False)

    #TODO use a templating instead
    @api.model
    def _prepare_availability_by_sms_notification(self):
        gateway = self.env['sms.gateway'].search([
            ('default_gateway', '=', True)], limit=1)
        return {
            'gateway_id': gateway.id,
            'message': _('Your picking %s is ready to transfer.') % self.name,
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
    def _get_send_picking_availability_by_sms_domain(self):
        return [
            ('state', '=', 'assigned'),
            ('availability_sent_by_sms', '=', False),
            ('picking_type_id.code', '=', 'outgoing'),
            ]

    @api.model
    def _cron_send_picking_availability_by_sms(self):
        domain = self._get_send_picking_availability_by_sms_domain()
        pickings = self.env['stock.picking'].search(domain)
        total = len(pickings)
        for idx, picking in enumerate(pickings):
            _logger.debug('Send Sms for picking %s, progress %s/%s', picking, idx, total)
            vals = picking._prepare_availability_by_sms_notification()
            self.env['sms.sms'].create(vals)
            picking.write({'availability_sent_by_sms': True})
            picking._cr.commit()
