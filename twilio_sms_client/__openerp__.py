# -*- coding: utf-8 -*-
# Copyright 2017 OpenSynergy Indonesia

{
    "name": "Twilio SMS Client",
    "version": "8.0.1.0.0",
    "license": "AGPL-3",
    "depends": ["mail",
                "base_sms_client",
                "base_suspend_security",
                "keychain",
                ],
    "external_dependency": {
        "python": [
            "twilio",
        ],
    },
    "author": "OpenSynergy Indonesia"
              "Odoo Community Association (OCA),Akretion",
              "website": "https://github.com/oca/connector-telephony",
    "category": "Tools",
    "data": [
        "data/keychain.xml",
    ],
    "installable": True,
}
