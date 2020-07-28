#    Copyright (C) 2013 Julius Network Solutions SARL <contact@julius.fr>
# Copyright (C) 2015 Sébastien BEAU <sebastien.beau@akretion.com>

{
    'name': 'OVH SMS Client',
    'version': '10.0.1.0.1',
    'license': 'AGPL-3',
    'depends': ['mail',
                'base_sms_client',
                'base_suspend_security',
                'keychain',
                ],
    'author': 'Julius Network Solutions,SYLEAM,'
              'Odoo Community Association (OCA),Akretion',
    'images': [
        'images/sms.jpeg',
        'images/gateway.jpeg',
        'images/gateway_access.jpeg',
        'images/client.jpeg',
        'images/send_sms.jpeg'
    ],
    'website': 'http://julius.fr',
    'category': 'Tools',
    'data': ['data/keychain.xml'],
    'installable': True,
}
