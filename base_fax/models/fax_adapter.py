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
import logging


_logger = logging.getLogger(__name__)


class FaxAdapter(models.Model):
    _name = 'fax.adapter'
    _description = 'Base Fax Adapter'
    
    @api.one
    def _compute_adapter_name(self, ):
        if self.adapter_pk:
            self.adapter_name = self._get_adapter().name
    
    transmission_ids = fields.One2many(
        comodel_name='fax.payload.transmission',
        inverse_name='adapter_id',
        string='Transmissions',
        help='Transmissions that have taken place over this adapter',
    )
    name = fields.Char(
        required=True
    )
    adapter_model_id = fields.Many2one(
        'ir.model',
        domain=[
            ('model', '=like', 'fax.%',),
            ('model', '!=', 'fax.adapter'),
        ],
        help='Proprietary fax adapter model',
    )
    adapter_model_name = fields.Char(
        related='adapter_model_id.model',
    )
    adapter_pk = fields.Integer(
        help='ID of the proprierary fax adapter',
    )
    adapter_name = fields.Char(
        compute='_compute_adapter_name',
    )
    country_id = fields.Many2one(
        'res.country',
        default=lambda s: s.env.user.company_id.country_id
    )
    company_id = fields.Many2one(
        'fax.adapter',
    )

    @api.multi
    def _get_adapter(self, ):
        self.ensure_one()
        adapter_obj = self.env[self.adapter_model_id.model]
        adapter_id = adapter_obj.browse(self.adapter_pk)
        _logger.debug('Got adapter model %s and obj %s',
                      adapter_obj, adapter_id)
        return adapter_id

    @api.one
    def _send(self, dialable, payload_ids, send_name=False, ):
        '''
        Sends payload using _send on proprietary adapter
        :param  dialable: str Number to fax to (convert_to_dial_number)
        :param  payload_ids: fax.payload record(s) To Send
        :param  send_name: str Name of person to send to
        '''
        adapter = self._get_adapter()
        transmission_vals = adapter._send(dialable, payload_ids, send_name)
        self.write({
            'transmission_ids': [(0, 0, transmission_vals)],
        })

    @api.one
    def _fetch_payloads(self, transmission_ids, ):
        '''
        Gets payloads using _fetch_payloads on proprietary adapter
        :param  transmission_ids: fax.payload.transmission To fetch for
        '''
        adapter = self._get_adapter()
        adapter._fetch_payloads(transmission_ids, )
    
