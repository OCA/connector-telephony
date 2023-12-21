# Copyright 2023 ForgeFlow S.L. (https://www.forgeflow.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "SMS Twilio",
    "summary": "Send sms using Twilio API",
    "version": "16.0.1.0.0",
    "category": "SMS",
    "website": "https://github.com/OCA/connector-telephony",
    "author": "Akretion, Odoo Community Association (OCA)",
    "maintainers": ["mariadforgeflow"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {"python": ["twilio"], "bin": []},
    "depends": ["base_phone", "sms", "iap_alternative_provider"],
    "data": [
        "views/iap_account_view.xml",
        "views/sms_sms_view.xml",
        "security/ir.model.access.csv",
    ],
}
