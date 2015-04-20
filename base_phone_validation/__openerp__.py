# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C)  Jordi Riera <kender.jr@gmail.com>
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
    'name': 'Base Phone Validation',
    'version': '1.0',
    'author': 'cgstudiomap, Odoo Community Association (OCA)',
    'maintainer': 'cgstudiomap',
    'license': 'AGPL-3',
    'category': 'Sale',
    'summary': 'Force the phone numbers to be valid.',
    'external_dependencies': {'python': ['phonenumbers']},
    'depends': ['base_phone'],
    'data': [],
    'installable': True,
}
