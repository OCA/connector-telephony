# -*- encoding: utf-8 -*-
##############################################################################
#
#    Asterisk Click2dial module for OpenERP
#    Copyright (C) 2010 Alexis de Lattre <alexis@via.ecp.fr>
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
    'version': '0.1',
    'category': 'Generic Modules/Others',
    'license': 'AGPL-3',
    'description': """This module adds a 'dial' button in the partner address
view so that users can directly dial a phone number through Asterisk. This feature is usually known as 'click2dial'.

Here is how it works :
1) In OpenERP, the user clicks on the 'dial' button next to a phone number field in the Partner address view.
2) Asterisk makes the user's phone ring.
3) The user answers his own phone (if he doesn't, the process stops here).
4) Asterisk dials the phone number found in OpenERP in place of the user.
5) If the remote party answers, the user can talk to his correspondent.

Documentation for this module is available on the Akretion Web site : http://www.akretion.com/""",
    'author': 'Alexis de Lattre',
    'website': 'http://www.akretion.com/',
    'depends': ['base'],
    'init_xml': [],
    'update_xml': ['asterisk_server_view.xml', 'res_users_view.xml', 'res_partner_view.xml', 'security/asterisk_server_security.xml'],
    'demo_xml': ['asterisk_click2dial_demo.xml'],
    'installable': True,
    'active': False,
}

