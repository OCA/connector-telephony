# -*- coding: utf-8 -*-
# (c) 2016 Trever L. Adams
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Asterisk Phone Log-call',
    'version': '9.0.1.0.0',
    'category': 'Phone',
    'license': 'AGPL-3',
    'summary': 'Necessary bridge between log-call and Asterisk Click2dial',
    'author': "Trever L. Adams",
    'website': '',
    'depends': ['logcall', 'asterisk_click2dial'],
    'data': [
        'security/ir.model.access.csv',
        'views/asterisk_server_view.xml',
    ],
    'application': True,
    'installable': True,
}
