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
    'version': '7.0.0.0.4',
    'category': 'Phone',
    'license': 'AGPL-3',
    'summary': 'FreeSWITCH-OpenERP connector',
    'description': """
FreeSWITCH-OpenERP connector
==========================

The technical name of this module is *freeswitch_click2dial*, but this module
implements much more than a simple *click2dial* ! This module adds 3
functionalities:

1) It adds a *Dial* button in the partner form view so that users can directly
   dial a phone number through FreeSWITCH. This feature is usually known as
   *click2dial*. Here is how it works :

    * In OpenERP, the user clicks on the *Dial* button next to a phone number
      field in the partner view.

    * OpenERP connects to the FreeSWITCH Event Socket and FreeSWITCH makes the
      user's phone ring.

    * The user answers his own phone (if he doesn't, the process stops here).

    * FreeSWITCH dials the phone number found in OpenERP in place of the user.

    * If the remote party answers, the user can talk to his correspondent.

2) It adds the ability to show the name of the calling party on the screen of
   your IP phone on incoming phone calls if the presented phone number is
   present in the partner/leads/employees/... of OpenERP. To understand how to
   use this, please see get_caller_name.py, which should be installed per the
   instructions in the script on the OpenERP/Odoo server. This works for
   incoming and outgoing calls, per instructions in the script.

3) It adds a phone icon (*Open Caller*) in the top menu bar
   (next to the Preferences) to get the partner/lead/candidate/registrations
   corresponding to the calling party in one click. Here is how it works :

    * When the user clicks on the phone icon, OpenERP sends a query to the
      FreeSWITCH Manager Interface to get a list of the current phone calls

    * If it finds a phone call involving the user's phone, it gets the phone
      number of the calling party

    * It searches the phone number of the calling party in the
      Partners/Leads/Candidates/Registrations of OpenERP. If a record matches,
      it takes you to the form view of this record. If no record matchs, it
      opens a wizard which proposes to create a new Partner with the presented
      phone number as *Phone* or *Mobile* number or update an existing Partner.

    It is possible to get a pop-up of the record corresponding to the calling
    party without any action from the user via the module *base_phone_popup*.

    Additionally, you will need the FreeSWITCH ESL python module. You will
    find it under ${FREESWITCH_SRC_TOP_DIR}/libs/esl/python. Go to
    ${FREESWITCH_SRC_TOP_DIR}/libs/esl. Type make. Then make pymod. You will
    then need to install ${FREESWITCH_SRC_TOP_DIR}/libs/esl/python/ESL.py and
    ${FREESWITCH_SRC_TOP_DIR}/libs/esl/python/_ESL.so into the appropriate
    places on your OpenERP/Odoo server.
    (https://wiki.freeswitch.org/wiki/Event_Socket_Library#Installation for
    more information.) An alternative method would involve
    https://github.com/gurteshwar/freeswitch-esl-python.

A detailed documentation for this module is available on the Akretion Web site:
http://www.akretion.com/products-and-services/openerp-freeswitch-voip-connector
""",
    'author': "Trever L. Adams,Akretion,Odoo Community Association (OCA)",
    'website': 'https://github.com/treveradams/connector-telephony',
    'depends': ['base_phone'],
    'external_dependencies': {'python': ['phonenumbers', 'ESL']},
    'data': [
        'freeswitch_server_view.xml',
        'res_users_view.xml',
        'security/ir.model.access.csv',
        ],
    'demo': ['freeswitch_click2dial_demo.xml'],
    'images': [
        'images/sshot-click2dial.jpg',
        'images/sshot-open_calling_party.jpg',
        ],
    'qweb': ['static/src/xml/*.xml'],
    'js': ['static/src/js/*.js'],
    'css': ['static/src/css/*.css'],
    'application': True,
    'installable': True,
    'active': False,
}
