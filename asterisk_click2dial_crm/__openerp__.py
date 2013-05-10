# -*- encoding: utf-8 -*-
##############################################################################
#
#    Asterisk click2dial CRM module for OpenERP
#    Copyright (c) 2011 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
#    Copyright (c) 2012-2013 Akretion (http://www.akretion.com)
#    Copyright (c) 2013 Invitu (http://www.invitu.com)
#    @author: Jesús Martín <jmartin@zikzakmedia.com>
#    @author: Alexis de Lattre <alexis.delattre@akretion.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
    "name": "Asterisk Click2dial CRM",
    "version": "0.1",
    "author": "Zikzakmedia SL, Akretion",
    "website": "http://www.zikzakmedia.com",
    "license" : "AGPL-3",
    "category": "Customer Relationship Management",
    "description": """
    This module adds CRM-specific features to the asterisk_click2dial module.

    It adds 2 features :

    First, when you do a click2dial, OpenERP will propose you to create an
    outbound phone call in the CRM ; if you answer 'Yes', it will create the phone
    call in the CRM and open it in a new tab. If some users don't want to be asked
    to create a phone call in the CRM each time they do a click2dial, you
    should disable the corresponding option in the 'Telephony' tab of the 'User'
    form.

    Second, when you receive a phone call and run the wizard "Open calling partner",
    if the partner is found in OpenERP, you will see a button that proposes to create
    an inbound phone call in the CRM.

    This module has been initially developped by Zikzakmedia and has been enhanced by Akretion.

    A detailed documentation for the OpenERP-Asterisk connector is available on the Akretion Web site : http://www.akretion.com/en/products-and-services/openerp-asterisk-voip-connector
    """,
    "depends": [
        'asterisk_click2dial',
        'crm',
    ],
    "init_xml": [],
    "demo_xml": [],
    "update_xml": [
        'wizard/open_calling_partner_view.xml',
        'wizard/create_crm_phonecall_view.xml',
        'res_users_view.xml',
	'crm_lead_view.xml',
    ],
    "installable": True,
}
