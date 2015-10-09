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


class SendFax(models.TransientModel):
    _name = 'fax.send_fax'
    _description = 'Wizard to send faxes'
    _inherit = ['phone.common']
    _phone_name_sequence = 10
    _country_field = 'country_id'
    _partner_field = None
    _phone_fields = ['fax_to_number']
    
    def _get_default_session(self, ):
        return self.env['fax.base'].browse(self._context.get('active_id'))

    fax_to_number = fields.Char(
        string='Fax To',
        help='Phone number of remote fax machine',
    )
    adapter_id = fields.Many2one(
        'fax.base',
        default=_get_default_session,
    )
    name = fields.Char(
        string="Fax Name",
    )
    image = fields.Binary(
        attachment=True,
    )
    country_id = fields.Many2one(
        'res.country',
        default=lambda s: s.env.user.company_id.country_id
    )
    
    @api.one
    def send_fax(self, ):
        payload_id = self.env['fax.payload'].create({
            'name': self.name,
            'image': self.image,
            'image_type': 'PNG',
        })
        number = self._generic_reformat_phonenumbers({
            'fax_to_number': self.fax_to_number,
        })
        number = number['fax_to_number']
        _logger.debug('Got number %s reformatted to %s',
                      self.fax_to_number, number)
        dialable = self.convert_to_dial_number(number)
        send_name = self.get_name_from_phone_number(number)
        self.adapter_id._send(dialable, payload_id, send_name)
