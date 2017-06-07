# -*- coding: utf-8 -*-
# © 2015 Valentin CHEMIERE <valentin.chemiere@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Sms Send Picking',
    'version': '8.0.1',
    'author': 'Akretion, Odoo Community Association (OCA)',
    'website': 'www.akretion.com',
    'license': 'AGPL-3',
    'category': 'Phone',
    'depends': [
        'stock',
        'smsclient_core',
    ],
    'data': [
        'cron.xml'
    ],
    'installable': True,
    'application': False,
}
