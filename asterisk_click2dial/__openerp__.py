# -*- coding: utf-8 -*-
# © 2010-2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Asterisk Click2dial',
    'version': '9.0.1.0.0',
    'category': 'Phone',
    'license': 'AGPL-3',
    'summary': 'Asterisk-Odoo connector',
    'author': "Akretion,Odoo Community Association (OCA)",
    'website': 'http://www.akretion.com/',
    'depends': ['base_phone'],
    'external_dependencies': {'python': ['Asterisk']},
    'data': [
        'asterisk_server_view.xml',
        'res_users_view.xml',
        'security/ir.model.access.csv',
        'web_asterisk_click2dial.xml',
        ],
    'demo': ['asterisk_click2dial_demo.xml'],
    'qweb': ['static/src/xml/*.xml'],
    'css': ['static/src/css/*.css'],
    'application': True,
    'installable': True,
}
