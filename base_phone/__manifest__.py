# -*- coding: utf-8 -*-
##############################################################################
#
#    Base Phone module for Odoo
#    Copyright (C) 2014-2015 Alexis de Lattre <alexis@via.ecp.fr>
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
    'name': 'Base Phone',
    'version': '10.0.0.1.0',
    'category': 'Phone',
    'license': 'AGPL-3',
    'summary': 'Validate phone numbers',
    'author': "Akretion,Odoo Community Association (OCA)",
    'website': 'http://www.akretion.com/',
    'depends': ['base_setup', 'web'],
    'external_dependencies': {'python': ['phonenumbers']},
    'data': [
        'security/phone_security.xml',
        'security/ir.model.access.csv',
        'views/res_partner_view.xml',
        'views/base_config_settings.xml',
        'views/res_users_view.xml',
        'wizard/reformat_all_phonenumbers_view.xml',
        'wizard/number_not_found_view.xml',
        'web_phone.xml',
        ],
    'qweb': ['static/src/xml/*.xml'],
    'images': [],
    'installable': True,
}
