# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Base Phone CDR",
    "category": "web",
    "version": "17.0.1.0.0",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/connector-telephony",
    "depends": ["base_phone_popup"],
    "data": [
        "view/phone_cdr_view.xml",
        "security/ir.model.access.csv",
        "view/res_users_view.xml",
        "view/res_partner_view.xml",
    ],
    "qweb": ["static/src/xml/widget.xml"],
    "license": "AGPL-3",
}
