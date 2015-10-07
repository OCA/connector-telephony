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
from openerp import models, fields


class FaxAdapter(models.AbstractModel):
    _name = 'fax.adapter'
    _description = 'Meant to be inherited by proprietary adapters'
    transmission_ids = fields.One2many(
        comodel_name='fax.payload.transmission',
        inverse_name='adapter_id',
        string='Transmissions',
        help='Transmissions that have taken place over this adapter',
    )
    name = fields.Char(
        required=True
    )

    def _send(self, fax_number, payload_id, ):
        '''
        Sends fax. Designed to be overridden in submodules
        :param  fax_number: str Number to fax to
        :param  payload_id: fax.payload To Send
        :return fax.payload.transmission: Representing fax transmission
        '''
        return False   # fax.payload.transmission record
