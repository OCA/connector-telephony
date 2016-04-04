# -*- encoding: utf-8 -*-
##############################################################################
#
#    Asterisk Click2dial module for Odoo
#    Copyright (C) 2010-2015 Alexis de Lattre <alexis@via.ecp.fr>
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
    'name': 'Asterisk Click2dial',
    'version': '9.0.0.1.0',
    'category': 'Phone',
    'license': 'AGPL-3',
    'summary': 'Asterisk-Odoo connector',
    'author': "Akretion,Odoo Community Association (OCA)",
    'website': 'http://www.akretion.com/',
    'depends': ['base_phone'],
    'external_dependencies': {'python': ['Asterisk']},
    'data': [
        'asterisk_server_view.xml',
        'res_users_view.xml',
        'security/ir.model.access.csv',
        'web_asterisk_click2dial.xml',
        ],
    'demo': ['asterisk_click2dial_demo.xml'],
    'qweb': ['static/src/xml/*.xml'],
    'css': ['static/src/css/*.css'],
    'application': True,
    'installable': False,
    'active': False,
}
