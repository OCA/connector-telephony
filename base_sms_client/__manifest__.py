# Copyright (C) 2015 Sébastien BEAU <sebastien.beau@akretion.com>
# © 2011 SYLEAM (<http://syleam.fr/>)
# © 2013 Julius Network Solutions SARL <contact@julius.fr>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{
    "name": "Base Sms Client",
    "version": "12.0.1.0.0",
    'license': 'AGPL-3',
    "depends": ['mail',
                'base_phone',
                ],
    'author': 'Julius Network Solutions,'
              'SYLEAM,'
              'Akretion,'
              'ACSONE SA/NV,'
              'Odoo Community Association (OCA)',
    'images': [
        'images/sms.jpeg',
        'images/gateway.jpeg',
        'images/gateway_access.jpeg',
        'images/client.jpeg',
        'images/send_sms.jpeg'
    ],
    "summary": "Sending SMSs very easily, individually or collectively.",
    "website": "https://github.com/OCA/connector-telephony",
    "category": "Phone",
    "data": [
        'wizards/sms_compose_message.xml',
        "data/ir_cron.xml",
        "security/groups.xml",
        "security/ir.model.access.csv",
        "security/sms_template.xml",
        "security/ir.rule.csv",
        "wizards/mass_sms_view.xml",
        "wizards/sms_template_preview.xml",
        "views/sms_gateway_view.xml",
        "views/sms_sms_view.xml",
        "views/server_action_view.xml",
        "views/sms_template_view.xml",
    ],
    "installable": True,
}
