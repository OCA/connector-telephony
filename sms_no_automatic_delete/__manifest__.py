# Copyright 2021 Akretion (http://www.akretion.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "No automatic deletion of SMS",
    "summary": "Avoid automatic delete of sended sms",
    "author": "Akretion,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/connector-telephony",
    "license": "AGPL-3",
    "category": "",
    "version": "14.0.1.0.0",
    "depends": ["sms"],
    "data": [
        "data/ir_cron_data.xml",
    ],
    "application": False,
    "installable": True,
}
