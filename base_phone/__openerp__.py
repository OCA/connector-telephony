# -*- encoding: utf-8 -*-
##############################################################################
#
#    Base Phone module for OpenERP
#    Copyright (C) 2014 Alexis de Lattre <alexis@via.ecp.fr>
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
    'name': 'Base Phone',
    'version': '0.1',
    'category': 'Extra Tools',
    'license': 'AGPL-3',
    'summary': 'Validate phone numbers',
    'description': """
Base Phone
==========

This module validate phone numbers using the phonenumbers Python library, which is a port of the lib used in Android smartphones. It also adds tel: links on phone numbers.

This module is independant from the Asterisk connector.

Please contact Alexis de Lattre from Akretion <alexis.delattre@akretion.com> for any help or question about this module.
""",
    'author': 'Akretion',
    'website': 'http://www.akretion.com/',
    'depends': ['base'],
    'external_dependencies': {'python': ['phonenumbers']},
    'data': [
        'res_partner_view.xml',
        'wizard/reformat_all_phonenumbers_view.xml',
        ],
    'js': [
        'static/src/js/*.js',
        'static/lib/js/*.js',
        ],
    'qweb': ['static/src/xml/*.xml'],
    'images': [],
    'installable': True,
    'active': False,
}
