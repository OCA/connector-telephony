# Copyright 2014-2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'HR Recruitment Phone',
    'version': '14.0.1.0.0',
    'category': 'Phone',
    'license': 'AGPL-3',
    'summary': 'Validate phone numbers in HR Recruitment',
    'author': "Akretion,Odoo Community Association (OCA)",
    'maintainers': ['alexis-via'],
    'website': 'https://github.com/OCA/connector-telephony',
    'depends': ['base_phone', 'hr_recruitment'],
    'data': [
        'security/ir.model.access.csv',
        ],
    'installable': True,
    'auto_install': True,
}
