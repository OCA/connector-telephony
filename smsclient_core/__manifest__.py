# coding: utf-8
# © 2004-2009 OpenERP SA (<http://openerp.com>)
# © 2011 SYLEAM (<http://syleam.fr/>)
# © 2013 Julius Network Solutions SARL <contact@julius.fr>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{
    "name": "SMS Client Core",
    "version": "10.0.1.0.0",
    "depends": ["base",
                "email_template",
                'base_phone',
                'keychain',
                ],
    'images': [
        'images/sms.jpeg',
        'images/gateway.jpeg',
        'images/gateway_access.jpeg',
        'images/client.jpeg',
        'images/send_sms.jpeg'
    ],
    "summary": """
Sending SMSs very easily, individually or collectively.

    """,
    "website": "http://julius.fr",
    "category": "Phone",
    "demo": [],
    "data": [
        "security/groups.xml",
        "security/ir.model.access.csv",
        "security/ir.rule.csv",
        "views/sms_gateway_view.xml",
        "views/serveraction_view.xml",
        "views/sms_gateway_data.xml",
        "wizard/mass_sms_view.xml",
        "views/smstemplate_view.xml"
    ],
    "installable": True,
}
