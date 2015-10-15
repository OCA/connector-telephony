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
from PIL import Image, ImageSequence
from io import BytesIO


class FaxPayload(models.Model):
    _name = 'fax.payload'
    _description = 'Fax Data Payload'

    name = fields.Char(
        help='Name of payload'
    )
    image_type = fields.Selection(
        [
            ('PNG', 'PNG'),
            ('JPG', 'JPG'),
            ('BMP', 'BMP'),
            ('GIF', 'GIF'),
            ('TIF', 'TIFF'),
        ],
        default='PNG',
        required=True,
        string='Image Format',
        help='Store image as this format',
    )
    transmission_ids = fields.Many2many(
        'fax.transmission',
        inverse_name='payload_ids',
    )
    page_ids = fields.One2many(
        'fax.payload.page',
        inverse_name='payload_id',
    )
    ref = fields.Char(
        readonly=True,
    )

    @api.one
    def _send(self, adapter_id, fax_number, ):
        '''
        Sends fax using specified adapter
        :param  adapter_id: fax.adapter to use
        :param  fax_number: str Number to fax to
        :return fax.transmission: Representing fax transmission
        '''
        return adapter_id._send(fax_number, self)

    @api.model
    def create(self, vals, ):
        '''
        Override Create method, inject a sequence ref and pages using `image`
        :param  vals['image']: str Raw image data, will convert to page_ids
        '''
        if vals.get('image'):
            images = self._convert_image(
                vals['image'], vals['image_type']
            )
            vals['page_ids'] = []
            for idx, img in enumerate(images):
                vals['page_ids'].append((0, 0, {
                    'name': '%02d.png' % idx,
                    'image': img,
                }))
            del vals['image'] # < The warning was killing my OCD
        vals['ref'] = self.env['ir.sequence'].next_by_code(
            'fax.payload'
        )
        return super(FaxPayload, self).create(vals)

    @api.one
    def write(self, vals, ):
        '''
        Override write to allow for image type conversions and page appends
        :param  vals['image_type']: str Will convert existing pages if needed
        :param  vals['image']: str Raw image data, will add as page_ids
        '''
        if vals.get('image_type'):
            if self.image_type != vals['image_type']:
                for img in self.page_ids:
                    img.image = self._convert_image(
                        img['image'], vals['image_type']
                    )
        if vals.get('image'):
            vals['page_ids'] = []
            image_type = vals.get('image_type') or self.image_type
            images = self._convert_image(vals['image'], image_type)
            for idx, img in enumerate(images):
                vals['page_ids'].append((0, 0, {
                    'name': '%02d.png' % idx,
                    'image': img,
                }))
            del vals['image'] # < The warning was killing my OCD
        super(FaxPayload, self).write(vals)

    def _convert_image(self, image, image_type, b64_out=True, b64_in=True):
        '''
        Convert image for storage and use by the fax adapter
        :param  image:  str Raw image data (binary or base64)
        :param  image_type: str
        :param  b64_out: bool
        :param  b64_in: bool
        :return images: list Of raw image data (pages)
        '''
        binary = image.decode('base64') if b64_in else image
        with BytesIO(binary) as raw_image:
            image = Image.open(raw_image)
            # prevent IOError: PIL doesn't support alpha for some formats
            if image_type in ['BMP', 'PDF']:
                if len(image.split()) == 4:
                    r, g, b, a = image.split()
                    image = Image.merge("RGB", (r, g, b))
            for frame in ImageSequence.Iterator(image):
                with BytesIO() as raw:
                    frame.save(raw, image_type)
                    val = raw.getvalue()
                    if b64_out:
                        val = val.encode('base64')
                    yield val
