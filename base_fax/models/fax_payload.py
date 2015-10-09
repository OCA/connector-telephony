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
from PIL import Image
from io import BytesIO


class FaxPayload(models.Model):
    _name = 'fax.payload'
    _description = 'Fax Data Payload'

    name = fields.Char(
        help='Name of image'
    )
    image = fields.Binary(
        string='Fax Image',
        attachment=True,
        #readonly=True,
        required=True,
    )
    image_type = fields.Selection(
        [
            ('PDF', 'PDF'),
            ('PNG', 'PNG'),
            ('JPG', 'JPG'),
            ('BMP', 'BMP'),
            ('GIF', 'GIF'),
        ],
        default='PNG',
        required=True,
        string='Image Format',
        help='Store image as this format',
    )
    # receipt_transmission_id = fields.One2many(
    #     'fax.payload.transmission',
    # )
    transmission_ids = fields.Many2many(
        'fax.payload.transmission',
        inverse_name='payload_ids',
    )
    ref = fields.Char(
        readonly=True,
    )

    @api.one
    def _send(self, adapter_id, fax_number, ):
        '''
        Sends fax using specified adapter
        :param  adapter_id: fax.base to use
        :param  fax_number: str Number to fax to
        :return fax.payload.transmission: Representing fax transmission
        '''
        return adapter_id._send(fax_number, self)

    @api.model
    def create(self, vals, ):
        if vals.get('image'):
            vals['image'] = self._convert_image(
                vals['image'], vals['image_type']
            )
        vals['ref'] = self.env['ir.sequence'].next_by_code(
            'fax.payload'
        )
        return super(FaxPayload, self).create(vals)

    @api.one
    def write(self, vals, ):
        if vals.get('image'):
            image_type = vals.get('image_type') or self.image_type
            vals['image'] = self._convert_image(
                vals['image'], image_type
            )
        elif vals.get('image_type'):
            vals['image'] = self._convert_image(
                self.image, image_type
            )
        super(FaxPayload, self).write(vals)

    def _convert_image(self, base64_encoded_image, image_type, b64_out=True):
        ''' Convert image for storage and use by the fax adapter '''
        binary = base64_encoded_image.decode('base64')
        with BytesIO(binary) as raw_image:
            image = Image.open(raw_image)
            with BytesIO() as new_raw:
                image.save(new_raw, image_type)
                val = new_raw.getvalue()
                if b64_out:
                    val = val.encode('base64')
                return val
