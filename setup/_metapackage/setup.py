import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo12-addons-oca-connector-telephony",
    description="Meta package for oca-connector-telephony Odoo addons",
    version=version,
    install_requires=[
        'odoo12-addon-asterisk_click2dial',
        'odoo12-addon-base_phone',
        'odoo12-addon-base_phone_popup',
        'odoo12-addon-connector_voicent',
        'odoo12-addon-crm_phone',
        'odoo12-addon-event_phone',
        'odoo12-addon-hr_phone',
        'odoo12-addon-hr_recruitment_phone',
        'odoo12-addon-sms_ovh_http',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
