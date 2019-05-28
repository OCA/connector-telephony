# Copyright (C) 2019 Open Source Integrators
# <https://www.opensourceintegrators.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Voicent Connector',
    'version': '12.0.1.0.0',
    'category': 'Connector',
    'license': 'AGPL-3',
    'summary': """This module allows you to connect Odoo with Voicent
    (https://www.voicent.com) and is meant to be extended to integrate
    Odoo records and processes with phone calls made by Voicent.""",
    "author": "Open Source Integrators, "
              "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/connector-telephony",
    'depends': [
        'connector',
    ],
    'data': [
        'security/ir.model.access.csv',
        'view/res_partner.xml',
        'view/backend_voicent.xml',
        'data/check_the_voicent_status.xml',
    ],
    'installable': True,
    'maintainers': [
        'max3903',
    ],
    'development_status': 'Beta',
}
