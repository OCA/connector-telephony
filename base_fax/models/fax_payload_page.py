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
from openerp import models, fields, api, tools


class FaxPayloadPage(models.Model):
    _name = 'fax.payload.page'
    _description = 'Fax Payload Page'

    @api.depends('image')
    def _compute_images(self):
        for rec in self:
            rec.image_xlarge = tools.image_resize_image_big(rec.image)
            rec.image_large = tools.image_resize_image(
                rec.image, (384, 384), 'base64', None, True
            )
            rec.image_medium = tools.image_resize_image_medium(rec.image)

    name = fields.Char(
        help='Name of image'
    )
    image = fields.Binary(
        string='Fax Image',
        attachment=True,
        # readonly=True,
        required=True,
    )
    image_xlarge = fields.Binary(
        string='XLarge Image (1024x1024)',
        compute='_compute_images',
        readonly=True,
        store=True,
        attachment=True,
    )
    image_large = fields.Binary(
        string='Large Image (384x384)',
        compute='_compute_images',
        readonly=True,
        store=True,
        attachment=True,
    )
    image_medium = fields.Binary(
        string='Medium Image (128x128)',
        compute='_compute_images',
        readonly=True,
        store=True,
        attachment=True,
    )
    payload_id = fields.Many2one(
        'fax.payload',
        inverse_name='page_ids',
    )
