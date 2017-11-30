# -*- coding: utf-8 -*-
# © 2015 Valentin CHEMIERE <valentin.chemiere@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Sms Send Picking',
    'version': '10.0.1.0.0',
    'author': 'Akretion, Odoo Community Association (OCA)',
    'website': 'www.akretion.com',
    'license': 'AGPL-3',
    'category': 'Phone',
    'depends': [
        'stock',
        'base_sms_client',
    ],
    'data': [
        'data/cron.xml'
    ],
    'installable': True,
    'application': False,
}
