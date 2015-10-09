# -*- encoding: utf-8 -*-
##############################################################################
#
#    Asterisk click2dial CRM module for OpenERP
#    Copyright (c) 2012-2014 Akretion (http://www.akretion.com)
#    @author: Alexis de Lattre <alexis.delattre@akretion.com>
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
    "name": "Asterisk Click2dial CRM",
    "version": "8.0.0.1.0",
    "author": "Akretion,Odoo Community Association (OCA)",
    "website": "http://www.akretion.com",
    "license": "AGPL-3",
    "category": "Phone",
    "description": """
Asterisk Click2dial CRM
=======================

This module is *EMPTY* ; so you should uninstall it now.
The code that used to be in this module has been moved to the module
*crm_phone* that is available in the same GitHub repository
https://github.com/OCA/connector-telephony

This module will be removed from the repository in the near future.
""",
    "depends": [
        'asterisk_click2dial',
        'crm_phone',
    ],
    "data": [],
    "installable": True,
    "application": False,
}
