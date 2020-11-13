{
    'name': "Base Phone CDR",
    'category': "web",
    'version': "12.0.1.0.1",
    'depends': ['base_phone_popup','web_notify'],
    'data': [
        'view/phone_cdr_view.xml',
        'security/ir.model.access.csv'
    ],
    'qweb': [
        'static/src/xml/widget.xml',
    ],
    'license': 'AGPL-3',
}
