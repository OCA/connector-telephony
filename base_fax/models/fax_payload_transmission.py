# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Dave Lasley <dave@laslabs.com>
#    Copyright: 2015 LasLabs, Inc.
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


class FaxPayloadTransmission(models.Model):
    _name = 'fax.payload.transmission'
    _description = 'Generic Fax Transmission Record Object'
    _inherit = ['phone.common']
    _phone_fields = ['remote_fax', 'local_fax']
    _phone_name_sequence = 10
    # _country_fields = 'country_id'
    #  _partner_field = None

    def _compute_status(self, ):
        ''' Compute Transmission Status '''
        pass

    remote_fax = fields.Char()
    local_fax = fields.Char()
    direction = fields.Selection(
        [
            ('in', 'Inbound'),
            ('out', 'Outbound'),
        ],
        default='in',
        string='Fax Direction',
        help='Whether transmission was incoming or outgoing',
    )
    status = fields.Selection(
        [
            ('draft', 'Draft'),
            ('transmit', 'Transmitted'),
            ('transmit_except', 'Exception'),
            ('done', 'Success'),
        ],
        readonly=True,
        required=True,
        default='draft',
        compute='_compute_status',
        help='Transmission Status',
    )
    timestamp = fields.Datetime(
        string='Transmission Timestamp',
    )
    response_num = fields.Text(
        help='API Response (Transmission) ID',
    )
    payload_id = fields.Many2one(
        comodel_name='fax.payload',
        required=True,
    )
    adapter_id = fields.Many2one(
        comodel_name='fax.adapter',
        required=True,
    )
    ref = fields.Char(
        readonly=True,
        required=True,
        default=lambda self: self.env['ir.sequence'].next_by_code(
            'fax.payload.transmission'
        )
    )
