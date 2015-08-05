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
    "name": "SMS Client Core",
    "version": "1.0",
    "depends": ["base",
                "email_template",
                'base_phone',
                ],
    "author": "Julius Network Solutions,SYLEAM,OpenERP SA,Akretion,"
              "Odoo Community Association (OCA)",
    'images': [
        'images/sms.jpeg',
        'images/gateway.jpeg',
        'images/gateway_access.jpeg',
        'images/client.jpeg',
        'images/send_sms.jpeg'
    ],
    "summary": """
Sending SMSs very easily, individually or collectively.

    """,
    "website": "http://julius.fr",
    "category": "Phone",
    "demo": [],
    "data": [
        "security/groups.xml",
        "security/ir.model.access.csv",
        "smsclient_view.xml",
        "serveraction_view.xml",
        "smsclient_data.xml",
        "wizard/mass_sms_view.xml",
        "partner_sms_send_view.xml",
        "smstemplate_view.xml"
    ],
    "active": False,
    "installable": True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
