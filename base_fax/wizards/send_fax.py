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


class SendFax(models.TransientModel):
    _name = 'send_fax'
    _description = 'Wizard to send faxes'
    
    def _default_session(self, ):
        return self.env['sale.rental'].browse(self._context.get('active_id'))

    fax_to = fields.Char(
        string='Fax To',
        help='Phone number of remote fax machine',
    )
    adapter_id = fields.Many2one(
        'fax.adapter',
    )
    