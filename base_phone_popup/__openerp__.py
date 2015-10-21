# -*- encoding: utf-8 -*-
##############################################################################
#
#    Base Phone Pop-up module for Odoo/OpenERP
#    Copyright (C) 2014 Alexis de Lattre <alexis@via.ecp.fr>
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
    'name': 'Base Phone Pop-up',
    'version': '8.0.0.4.0',
    'category': 'Phone',
    'license': 'AGPL-3',
    'summary': 'Pop-up the related form view to the user on incoming calls',
    'description': """
Base Phone Pop-up
=================

When the user receives a phone call, Odoo can automatically open the
corresponding partner/lead/employee/... in a pop-up without any action from the
user.

The module *web_action_request* can be downloaded with Mercurial:

hg clone http://bitbucket.org/anybox/web_action_request

Warning : proxying WebSockets is only supported since Nginx 1.3.13 ; the
feature provided by this module won't work with older versions of Nginx.
""",
    'author': "Akretion,Odoo Community Association (OCA)",
    'website': 'http://www.akretion.com/',
    'depends': ['base_phone', 'web_action_request'],
    'data': ['res_users_view.xml'],
}
