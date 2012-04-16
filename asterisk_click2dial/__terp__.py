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
    'version': '0.3',
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

This module also adds the ability to show the name of the calling party on incoming phone calls if the presented
phone number is present in the Partner addresses of OpenERP.

Here is how it works :
1) On incoming phone calls, the Asterisk dialplan executes an AGI "get_cid_name_timeout.sh".
2) The "get_cid_name_timeout.sh" script calls the "get_cid_name.py" script with a short timeout.
3) The "get_cid_name.py" script will make an XML-RPC request on the OpenERP server to try to find the name
   of the person corresponding to the phone number presented by the calling party.
4) If it finds the name, it is add as CallerID name of the call, so as to be presented on the IP phone
   of the user.

A detailed documentation for this module is available on the Akretion Web site : http://www.akretion.com/en/products-and-services/openerp-asterisk-voip-connector """,
    'author': 'Akretion',
    'website': 'http://www.akretion.com/',
    'depends': ['base'],
    'init_xml': [],
    'update_xml': ['asterisk_server_view.xml', 'res_users_view.xml', 'res_partner_view.xml', 'security/asterisk_server_security.xml'],
    'demo_xml': ['asterisk_click2dial_demo.xml'],
    'installable': True,
    'active': False,
}

