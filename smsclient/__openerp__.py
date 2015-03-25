# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 OpenERP SA (<http://openerp.com>)
#    Copyright (C) 2011 SYLEAM (<http://syleam.fr/>)
#    Copyright (C) 2013 Julius Network Solutions SARL <contact@julius.fr>
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
    "name": "SMS Client",
    "version": "1.0",
    "depends": ["base",
                "email_template",
                ],
    "author": "Julius Network Solutions,SYLEAM,OpenERP SA",
    'images': ['images/sms.jpeg', 'images/gateway.jpeg', 'images/gateway_access.jpeg','images/client.jpeg','images/send_sms.jpeg'],
    "description": """
SMS Client module provides:
-------------
Sending SMSs very easily, individually or collectively.

*Generalities

OpenERP does not directly generate the SMS you will have to subscribe to an operator with a web interface (Type OVH) or via a URL generation.
If you want to use a 'SMPP Method' you must have to install the library "Soap" which can be installed with: apt-get install python-soappy.
You can find it on https://pypi.python.org/pypi/SOAPpy/
You don't need it if you use a "HTTP Method' to send the SMS.

*Use Multiple Gateways.

The Gateway configuration is performed directly in the configuration menu. For each gateway, you have to fill in the information for your operator.

To validate Gateway, code is send to a mobile phone, when received enter it to confirm SMS account.

This Module was developped by SYLEAM and OpenERP SA in a first place.
Then, it was updated to the 7.0 version by Julius Network Solutions.
    """,
    "website": "http://julius.fr",
    "category": "Tools",
    "demo": [],
    "data": [
        "security/groups.xml",
        "security/ir.model.access.csv",
        "smsclient_view.xml",
        "serveraction_view.xml",
#        "smsclient_wizard.xml",
        "smsclient_data.xml",
        "wizard/mass_sms_view.xml",
        "partner_sms_send_view.xml",
        "smstemplate_view.xml"
    ],
    "active": False,
    "installable": True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
