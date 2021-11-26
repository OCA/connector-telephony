import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo14-addons-oca-connector-telephony",
    description="Meta package for oca-connector-telephony Odoo addons",
    version=version,
    install_requires=[
        'odoo14-addon-asterisk_click2dial',
        'odoo14-addon-base_phone',
        'odoo14-addon-crm_phone',
        'odoo14-addon-event_phone',
        'odoo14-addon-hr_phone',
        'odoo14-addon-hr_recruitment_phone',
        'odoo14-addon-sms_no_automatic_delete',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 14.0',
    ]
)
