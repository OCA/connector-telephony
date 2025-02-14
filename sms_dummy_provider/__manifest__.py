# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

{
    "name": "SMS provider: Messagebird",
    "summary": "Send SMS via messagebird.com",
    "version": "16.0.1.0.0",
    "development_status": "Alpha",
    "category": "Tools",
    "website": "https://github.com/OCA/connector-telephony",
    "author": "Hunki Enterprises BV, Odoo Community Association (OCA)",
    "maintainers": ["hbrunn"],
    "license": "AGPL-3",
    "depends": [
        "sms_alternative_provider",
    ],
    "data": [
        "views/ir_sms_gateway.xml",
    ],
}
