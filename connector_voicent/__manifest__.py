# @TODO: To use the right License.
# @TODO: Description, Website, Contributros..etc.
{
    'name': 'Voicent Connector',
    'version': '12.0.1.0.0',
    'category': 'Phone',
    'license': 'AGPL-3',
    'summary': 'Automate phone calls based on stage changes',
    'development_status': 'Stable',
    'maintainers': [
        'younessmaafi',
        'max3903',
    ],
    'author': 'Maxime Chambreuil, Youness MAAFI,'
              ' Odoo Community Association (OCA)',
    'website': 'http://opensourceintegrators.com',
    'depends': [
        'base',
        ],
    'data': [
        # Security
        'security/ir.model.access.csv',
        # Views
        'view/res_partner.xml',
        'view/backend_voicent.xml',
        ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}
