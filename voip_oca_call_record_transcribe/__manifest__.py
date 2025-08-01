# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Voip OCA Call Record Transcribe",
    "summary": "Extends VoIP OCA to transcribe record calls",
    "version": "18.0.1.0.0",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/connector-telephony",
    "license": "AGPL-3",
    "category": "Productivity/VOIP",
    "excludes": ["voip"],
    "depends": ["voip_oca_call_record"],
    "maintainers": ["jordibforgeflow"],
    "data": [
        "views/voip_call_views.xml",
        "views/voip_pbx_views.xml",
        "data/service_cron.xml",
    ],
    "installable": True,
}
