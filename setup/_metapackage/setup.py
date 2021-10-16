import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo11-addons-oca-connector-telephony",
    description="Meta package for oca-connector-telephony Odoo addons",
    version=version,
    install_requires=[
        'odoo11-addon-asterisk_click2dial',
        'odoo11-addon-base_phone',
        'odoo11-addon-crm_phone',
        'odoo11-addon-event_phone',
        'odoo11-addon-hr_phone',
        'odoo11-addon-hr_recruitment_phone',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 11.0',
    ]
)
