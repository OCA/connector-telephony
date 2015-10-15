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
    def _compute_images(self, ):
        for rec in self:
            rec.image_medium = tools.image_resize_image_medium(rec.image)
            rec.image_small = tools.image_resize_image_small(rec.image)

    name = fields.Char(
        help='Name of image'
    )
    image = fields.Binary(
        string='Fax Image',
        attachment=True,
        # readonly=True,
        required=True,
    )
    image_medium = fields.Binary(
        string='Medium Image',
        compute='_compute_images',
        store=True,
        attachment=True,
    )
    image_small = fields.Binary(
        string='Small Image',
        compute='_compute_images',
        store=True,
        attachment=True,
    )
    payload_id = fields.Many2one(
        'fax.payload',
        inverse_name='page_ids',
    )
