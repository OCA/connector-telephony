# -*- coding: utf-8 -*-
##############################################################################
#
#    FreeSWITCH Click2dial module for OpenERP
#    Copyright (C) 2010-2014 Alexis de Lattre <alexis@via.ecp.fr>
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
    'name': 'FreeSWITCH Click2dial',
    'version': '8.0.0.4.0',
    'category': 'Phone',
    'license': 'AGPL-3',
    'summary': 'FreeSWITCH-OpenERP connector',
    'author': "Trever L. Adams,Akretion,Odoo Community Association (OCA)",
    'website': 'https://github.com/treveradams/connector-telephony',
    'depends': ['base_phone'],
    'external_dependencies': {'python': ['ESL']},
    'data': [
        'freeswitch_server_view.xml',
        'res_users_view.xml',
        'security/ir.model.access.csv',
        'web_freeswitch_click2dial.xml',
        ],
    'demo': ['freeswitch_click2dial_demo.xml'],
    'qweb': ['static/src/xml/*.xml'],
    'css': ['static/src/css/*.css'],
    'application': True,
    'installable': True,
}
