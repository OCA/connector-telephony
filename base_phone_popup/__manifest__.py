# Copyright 2014-2016 Akretion, Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Base Phone Pop-up',
    'version': '11.0.1.0.0',
    'category': 'Phone',
    'license': 'AGPL-3',
    'summary': 'Pop-up the related form view to the user on incoming calls',
    'author': "Akretion,Odoo Community Association (OCA)",
    'website': 'https://github.com/OCA/connector-telephony/',
    'depends': [
        'crm_phone_validation',
    ],
    'data': [
        'views/res_users_view.xml',
    ],
    'installable': True,
}
