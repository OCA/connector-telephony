import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo8-addons-oca-connector-telephony",
    description="Meta package for oca-connector-telephony Odoo addons",
    version=version,
    install_requires=[
        'odoo8-addon-asterisk_click2dial',
        'odoo8-addon-asterisk_click2dial_crm',
        'odoo8-addon-base_phone',
        'odoo8-addon-base_phone_popup',
        'odoo8-addon-crm_claim_phone',
        'odoo8-addon-crm_phone',
        'odoo8-addon-event_phone',
        'odoo8-addon-hr_phone',
        'odoo8-addon-hr_recruitment_phone',
        'odoo8-addon-ovh_telephony_connector',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 8.0',
    ]
)
