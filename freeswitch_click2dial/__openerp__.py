# -*- coding: utf-8 -*-
# (c) 2010-2014 Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html


{
    'name': 'FreeSWITCH Click2dial',
    'version': '8.0.0.4.0',
    'category': 'Phone',
    'license': 'AGPL-3',
    'summary': 'FreeSWITCH-OpenERP connector',
    'author': "Trever L. Adams,Akretion,Odoo Community Association (OCA)",
    'website': 'https://github.com/treveradams/connector-telephony',
    'depends': ['base_phone'],
    'external_dependencies': {'python': ['freeswitchESL']},
    'data': [
        'freeswitch_server_view.xml',
        'res_users_view.xml',
        'security/ir.model.access.csv',
        'web_freeswitch_click2dial.xml',
        ],
    'demo': ['freeswitch_click2dial_demo.xml'],
    'qweb': ['static/src/xml/*.xml'],
    'css': ['static/src/css/*.css'],
    'application': True,
    'installable': True,
}
