# -*- encoding: utf-8 -*-
##############################################################################
#
#    Asterisk click2dial Registration module for OpenERP
#    Copyright (C) 2013 Invitu <contact@invitu.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
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
    "name": "Asterisk Click2dial Registration",
    "version": "0.1",
    "author": "INVITU",
    "website": "http://www.invitu.com",
    "license": "AGPL-3",
    "category": "Extra Tools",
    "description": """
    This module adds a button "Open Registrations" on the "Open calling partner" wizard and a "Dial" button on the Registration form.

    A detailed documentation for the OpenERP-Asterisk connector is available on the Akretion Web site : http://www.akretion.com/open-source-contributions/openerp-asterisk-voip-connector
    """,
    "depends": [
        'asterisk_click2dial',
        'event',
    ],
    "demo": [],
    "data": [
        'wizard/open_calling_partner_view.xml',
        'registration_view.xml',
    ],
    "installable": True,
    "application": True,
}
