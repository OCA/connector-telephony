# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Dave Lasley <dave@laslabs.com>
#    Copyright: 2015 LasLabs, Inc [https://laslabs.com]
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
{
    'name': 'Extension to base_phone providing fax core',
    'version': '8.0.0.1',
    'category': 'Phone',
    'author': "LasLabs, Odoo Community Association (OCA)",
    'license': 'AGPL-3',
    'website': 'https://github.com/OCA/connector-telephony',
    'depends': [
        'base_phone',
    ],
    'data': [
        'security/fax_security.xml',
        'security/ir.model.access.csv',
        'views/fax_payload_view.xml',
        'views/fax_transmission_view.xml',
        'views/res_company_view.xml',
        'views/fax_menus.xml',
        'wizard/send_fax_view.xml',
        'data/ir_sequence.xml',
    ],
    'installable': True,
    'application': False,
}
