# Copyright 2025 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Voip OCA",
    "summary": "Provides the use of Voip",
    "version": "17.0.1.0.2",
    "author": "Dixmit, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/connector-telephony",
    "license": "AGPL-3",
    "category": "Productivity/VOIP",
    "excludes": ["voip"],
    "depends": ["mail"],
    "maintainers": ["etobella"],
    "data": [
        "security/ir.model.access.csv",
        "views/res_users.xml",
        "views/voip_call.xml",
        "views/voip_pbx.xml",
        "views/menus.xml",
    ],
    "demo": ["demo/demo_data.xml"],
    "assets": {
        "web.assets_backend": [
            "voip_oca/static/src/**/*",
        ],
        "voip_oca.agent_assets": [
            "voip_oca/static/lib/*.js",
        ],
        "web.qunit_suite_tests": [
            "voip_oca/static/tests/web/**/*.esm.js",
        ],
        "web.tests_assets": [
            "voip_oca/static/tests/helpers/**/*.esm.js",
        ],
    },
}
