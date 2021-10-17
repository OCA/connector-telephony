import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo10-addons-oca-connector-telephony",
    description="Meta package for oca-connector-telephony Odoo addons",
    version=version,
    install_requires=[
        'odoo10-addon-asterisk_click2dial',
        'odoo10-addon-base_phone',
        'odoo10-addon-base_phone_popup',
        'odoo10-addon-base_sms_client',
        'odoo10-addon-crm_phone',
        'odoo10-addon-event_phone',
        'odoo10-addon-hr_phone',
        'odoo10-addon-hr_recruitment_phone',
        'odoo10-addon-ovh_sms_client',
        'odoo10-addon-sms_send_picking',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 10.0',
    ]
)
