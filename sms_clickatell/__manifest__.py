# Copyright 2020 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "SMS Clickatell",
    "summary": """
        Send SMS with Clickatell instead of Odoo SA IAP.""",
    "version": "13.0.1.0.0",
    "license": "AGPL-3",
    "author": "RPSJR,Odoo Community Association (OCA)",
    "website": "https://github.com/oca/connector-telephony",
    "depends": ["sms", "iap"],  # Odoo SA.
    "data": ["views/iap_account.xml"],
    "demo": [],
}
