# -*- encoding: utf-8 -*-
##############################################################################
#
#    Asterisk Click2dial module for OpenERP
#    Copyright (C) 2010-2012 Alexis de Lattre <alexis@via.ecp.fr>
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
    'description': """This module adds 3 functionnalities :

1) It adds a 'dial' button in the partner address form view so that users can directly dial a phone number through Asterisk. This feature is usually known as 'click2dial'. Here is how it works :
. In OpenERP, the user clicks on the 'dial' button next to a phone number field in the partner address view.
. OpenERP connects to the Asterisk Manager Interface and Asterisk makes the user's phone ring.
. The user answers his own phone (if he doesn't, the process stops here).
. Asterisk dials the phone number found in OpenERP in place of the user.
. If the remote party answers, the user can talk to his correspondent.

2) It adds the ability to show the name of the calling party on the screen of your IP phone on incoming phone calls if the presented
phone number is present in the partner addresses of OpenERP. Here is how it works :
. On incoming phone calls, the Asterisk dialplan executes an AGI script "get_cid_name_timeout.sh".
. The "get_cid_name_timeout.sh" script calls the "get_cid_name.py" script with a short timeout.
. The "get_cid_name.py" script will make an XML-RPC request on the OpenERP server to try to find the name of the person corresponding to the phone number presented by the calling party.
. If it finds the name, it is set as the CallerID name of the call, so as to be presented on the IP phone of the user.

3) It adds a button "Open calling partner" in the menu "Sales > Address book" to open the partner form of the calling party in 2 clicks. Here is how it works :
. When the user clicks on the "Open calling partner" button, OpenERP sends a query to the Asterisk Manager Interface to get a list of the current phone calls
. If it finds a phone call involving the user's phone, it gets the phone number of the calling party
. It searches the phone number of the calling party in the Partner addresses of OpenERP and, if a record matches, it opens the form view of the corresponding partner.

A detailed documentation for this module is available on the Akretion Web site : http://www.akretion.com/en/products-and-services/openerp-asterisk-voip-connector """,
    'author': 'Akretion',
    'website': 'http://www.akretion.com/',
    'depends': ['base'],
    'init_xml': [],
    'update_xml': [
        'asterisk_server_view.xml',
        'res_users_view.xml',
        'res_partner_view.xml',
        'security/asterisk_server_security.xml',
        ],
    'demo_xml': ['asterisk_click2dial_demo.xml'],
    'installable': True,
    'active': False,
}

