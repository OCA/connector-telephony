{
    "name": "Connector Phone CloudCTI Event Manager",
    "category": "web",
    "summary": "This module integrates odoo with Phone Connector CloudCTI.",
    "version": "17.0.1.0.0",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/field-service",
    "depends": ["base_phone_cdr", "inputmask_widget", "sale", "stock","crm", 'sale_crm'],
    "data": [
        "views/res_company.xml",
        "views/res_users_view.xml",
        "views/res_partner_views.xml",
        "views/phone_cdr_view.xml",
        "views/sale_order_views.xml",
        "views/stock_picking_views.xml",
        "views/crm_views.xml",
    ],
    'assets': {
        'web.assets_backend': [

            "connector_phone_cloudcti_event_manager/static/src/services/*.js",
            # 'connector_phone_cloudcti_event_manager/static/src/core/**/*'
            # 'connector_phone_cloudcti_event_manager/static/src/js/widget.js',
            # 'connector_phone_cloudcti_event_manager/static/src/js/notification_widget.js',
        ]
    },
    # "qweb": ["static/src/xml/widget.xml"],
    "license": "AGPL-3",
    "external_dependencies": {"python": ["phonenumbers"]},
}
