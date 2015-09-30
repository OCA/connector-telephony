# -*- encoding: utf-8 -*-
##############################################################################
#
#    OVH Connector module for Odoo
#    Copyright (C) 2015 Alexis de Lattre <alexis@via.ecp.fr>
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
    'name': 'OVH Telephony Connector',
    'version': '0.2',
    'category': 'Phone',
    'license': 'AGPL-3',
    'summary': 'OVH-Odoo telephony connector (click2call)',
    'author': 'Akretion',
    'website': 'http://www.akretion.com/',
    'depends': ['base_phone'],
    'external_dependencies': {'python': ['phonenumbers', 'SOAPpy']},
    'data': [
        'res_users_view.xml',
        ],
    'demo': [],
    'qweb': ['static/src/xml/*.xml'],
    'application': True,
    'installable': True,
}
