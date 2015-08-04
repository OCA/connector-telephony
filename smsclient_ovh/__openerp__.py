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
    "name": "SMS Client OVH",
    "version": "1.0",
    "depends": ["base",
                "email_template",
                "smsclient_core",
                ],
    "author": "Julius Network Solutions,SYLEAM,OpenERP SA,OCA,Akretion",
    'images': [
        'images/sms.jpeg',
        'images/gateway.jpeg',
        'images/gateway_access.jpeg',
        'images/client.jpeg',
        'images/send_sms.jpeg'
    ],
    "website": "http://julius.fr",
    "category": "Tools",
    "demo": [],
    "data": [
    ],
    "active": False,
    "installable": True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
