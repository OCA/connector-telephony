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


class FaxBase(models.Model):
    _name = 'fax.base'
    _description = 'Fax Base'
    
    @api.one
    def _compute_adapter_name(self, ):
        if self.adapter_pk:
            self.adapter_name = self.__get_adapter().name
    
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
        domain=[('model', '=like', 'fax.%',)],
        help='Proprietary fax adapter model',
    )
    adapter_model_name = fields.Char(
        related='adapter_model_id.name',
    )
    adapter_pk = fields.Integer(
        help='ID of the proprierary fax adapter',
    )
    adapter_name = fields.Char(
        compute='_compute_adapter_name',
    )

    @api.multi
    def __get_adapter(self, ):
        self.ensure_one()
        return self.adapter_model_id.browse(self.adapter_pk)

    @api.multi
    def _send(self, fax_number, payload_ids, ):
        '''
        Sends payload using _send on proprietary adapter
        :param  fax_number: str Number to fax to
        :param  payload_ids: fax.payload record(s) To Send
        :return fax.payload.transmission: Representing fax transmission
        '''
        self.ensure_one()
        adapter = self.__get_adapter()
        transmission = adapter._send(fax_number, payload_ids, )
        transmission.action_transmit()

    @api.multi
    def _get_transmission_status(self, transmission_id, ):
        '''
        Returns _get_transmission_status from proprietary adapter
        :param  transmission_id: fax.payload.transmission To Check On
        :return (transmission_status: str, status_msg: str)
        '''
        self.ensure_one()
        adapter = self.__get_adapter()
        return adapter._get_transmission_status(transmission_id, )
    
