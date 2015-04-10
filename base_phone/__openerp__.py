# -*- encoding: utf-8 -*-
##############################################################################
#
#    Base Phone module for OpenERP
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
    'name': 'Base Phone',
    'version': '0.1',
    'category': 'Phone',
    'license': 'AGPL-3',
    'summary': 'Validate phone numbers',
    'author': "Akretion,Odoo Community Association (OCA)",
    'website': 'http://www.akretion.com/',
    'depends': ['web'],
    'external_dependencies': {'python': ['phonenumbers']},
    'data': [
        'security/phone_security.xml',
        'security/ir.model.access.csv',
        'res_partner_view.xml',
        'res_company_view.xml',
        'res_users_view.xml',
        'wizard/reformat_all_phonenumbers_view.xml',
        'wizard/number_not_found_view.xml',
        'web_phone.xml',
        ],
    'qweb': ['static/src/xml/*.xml'],
    'demo': ['base_phone_demo.xml'],
    'test': ['test/phonenum.yml'],
    'images': [],
    'installable': True,
}
