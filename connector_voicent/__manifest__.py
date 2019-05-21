# @TODO: To use the right License.
# @TODO: Description, Website, Contributros..etc, of this module to be adjusted later. 
{
    'name': 'Voicent Connector',
    'version': '12.0.1.0.0',
    'category': 'Phone',
    'license': 'AGPL-3',
    'summary': 'Voicent Connector',
    'description': """
Voicent Connector
=========
Usage:
    Go to Connectors > Backends > Voicent Backends
    Create a new Voicent Backend with the host and port
    Create Call Lines to determine when (which stage in the process) calls are added to the queue
    Create Time Line to determine when (what time) calls are made
""",
    'author': "Maxime Chambreuil, Youness MAAFI, Odoo Community Association (OCA)",
    'website': 'http://opensourceintegrators.com',
    'depends': [
        'base',
        'crm',
        'base_phone',
        'crm_phone_validation'
        ],
    'external_dependencies': {'python': ['phonenumbers']},
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