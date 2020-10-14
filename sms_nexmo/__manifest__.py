# Copyright 2020 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Sms Nexmo',
    'summary': """
        Send SMS with Nexmo instead of Odoo SA IAP.""",
    'version': '13.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'KMEE,Odoo Community Association (OCA)',
    'website': 'https://github.com/oca/connector-telephony',
    'depends': [
        'sms', # Odoo SA.
        'iap',
    ],
    'data': [
        'views/iap_account.xml',
    ],
    'demo': [
    ],
}
