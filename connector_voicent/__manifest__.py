# Copyright (C) 2019 Open Source Integrators
# <https://www.opensourceintegrators.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Voicent Connector',
    'version': '12.0.1.0.0',
    'category': 'Connector',
    'license': 'AGPL-3',
    'summary': """Connect Odoo with Voicent""",
    "author": "Open Source Integrators, "
              "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/connector-telephony",
    'depends': [
        'connector',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_cron.xml',
        'views/res_partner.xml',
        'views/backend_voicent_call_line.xml',
        'views/backend_voicent.xml',
    ],
    'installable': True,
    'maintainers': [
        'max3903',
    ],
    'development_status': 'Beta',
}
