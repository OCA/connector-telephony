import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo9-addons-oca-connector-telephony",
    description="Meta package for oca-connector-telephony Odoo addons",
    version=version,
    install_requires=[
        'odoo9-addon-asterisk_click2dial',
        'odoo9-addon-base_phone',
        'odoo9-addon-base_phone_popup',
        'odoo9-addon-crm_phone',
        'odoo9-addon-event_phone',
        'odoo9-addon-hr_phone',
        'odoo9-addon-hr_recruitment_phone',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 9.0',
    ]
)
