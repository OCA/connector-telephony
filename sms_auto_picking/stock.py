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

from openerp import api, models
from openerp.osv import fields


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def _get_pickings(self, cr, uid, ids, context=None):
        res = set()
        for move in self.browse(cr, uid, ids, context=context):
            if move.picking_id:
                res.add(move.picking_id.id)
        return list(res)

    def _state_get(self, cr, uid, ids, field_name, args, context=None):
        res = super(StockPicking, self)._state_get(cr, uid, ids, field_name, args, context)
        sms_sender_obj = self.pool.get('partner.sms.send')
        gateway_obj = self.pool.get('sms.smsclient')
        gateway_ids = gateway_obj.search(cr, uid, [('default_gateway', '=', True)])
        gateway = gateway_obj.browse(cr, uid, gateway_ids[0])
        for pick in self.browse(cr, uid, ids):
            import ipdb; ipdb.set_trace()
            if res[pick.id] == 'assigned':
                data = {
                    'gateway': gateway_ids[0],
                    'text': 'Your picking %s is ready to transfert' % pick.name,
                    'mobile_to': pick.partner_id.phone,
                }
                sms_sender_id = sms_sender_obj.create(cr, uid, data)
                sms_sender_obj.browse(cr, uid, sms_sender_id).sms_send()
        return res

    _columns = {
        'state': fields.function(_state_get, type="selection", copy=False,
            store={
                'stock.picking': (lambda self, cr, uid, ids, ctx: ids, ['move_type'], 20),
                'stock.move': (_get_pickings, ['state', 'picking_id', 'partially_available'], 20)},
            selection=[
                ('draft', 'Draft'),
                ('cancel', 'Cancelled'),
                ('waiting', 'Waiting Another Operation'),
                ('confirmed', 'Waiting Availability'),
                ('partially_available', 'Partially Available'),
                ('assigned', 'Ready to Transfer'),
                ('done', 'Transferred'),
                ], string='Status', readonly=True, select=True, track_visibility='onchange',
            help="""
                * Draft: not confirmed yet and will not be scheduled until confirmed\n
                * Waiting Another Operation: waiting for another move to proceed before it becomes automatically available (e.g. in Make-To-Order flows)\n
                * Waiting Availability: still waiting for the availability of products\n
                * Partially Available: some products are available and reserved\n
                * Ready to Transfer: products reserved, simply waiting for confirmation.\n
                * Transferred: has been processed, can't be modified or cancelled anymore\n
                * Cancelled: has been cancelled, can't be confirmed anymore"""
        ),
    }
