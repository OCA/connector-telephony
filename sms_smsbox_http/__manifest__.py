# Copyright 2026 INVITU (<https://www.invitu.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "SMS SMSBOX HTTP",
    "summary": "SMS gateway for the SMSBOX HTTP API",
    "version": "18.0.1.0.0",
    "category": "Tools",
    "website": "https://github.com/OCA/connector-telephony",
    "author": "INVITU, Odoo Community Association (OCA)",
    "maintainers": ["cvinh"],
    "license": "AGPL-3",
    "depends": ["iap_alternative_provider", "sms_alternative_provider"],
    "data": [
        "data/iap_service_data.xml",
        "views/iap_account_views.xml",
        "views/ir_sms_gateway_views.xml",
    ],
    "installable": True,
}
