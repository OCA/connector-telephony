# -*- coding: utf-8 -*-
# (c) 2016 credativ ltd. - Ondřej Kuzník
# (c) 2016 Trever L. Adams
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html


{
    'name': 'Phone Log-call',
    'version': '9.0.1.0.0',
    'category': 'Phone',
    'license': 'AGPL-3',
    'summary': 'Allow a call to be logged in Odoo',
    'author': "credativ Ltd,Odoo Community Association (OCA)",
    'website': 'http://www.credativ.co.uk/',
    'depends': ['base_phone', 'crm_phone'],
    'data': [
        'security/phone_integration_security.xml',
        'security/ir.model.access.csv',
        'views/crm_phonecall_view.xml',
        'views/res_users_view.xml'
    ],
    'application': True,
    'installable': True,
}
