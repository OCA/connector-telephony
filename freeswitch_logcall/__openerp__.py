# -*- coding: utf-8 -*-
##############################################################################
#
#    Phone Log-call module for Odoo/OpenERP
#    Copyright (C) 2016 credativ Ltd (<http://credativ.co.uk>).
#    Copyright (C) 2016 Trever L. Adams
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
    'name': 'FreeSwitch Phone Log-call',
    'version': '9.0.0.1.0',
    'category': 'Phone',
    'license': 'AGPL-3',
    'summary': 'Necessary bridge between log-call and FreeSWITCH Click2dial',
    'author': "Trever L. Adams",
    'website': '',
    'depends': ['logcall', 'freeswitch_click2dial'],
    'data': [
        'security/ir.model.access.csv',
        'views/freeswitch_server_view.xml',
    ],
    'application': True,
    'installable': True,
}
