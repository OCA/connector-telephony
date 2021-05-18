import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo14-addons-oca-connector-telephony",
    description="Meta package for oca-connector-telephony Odoo addons",
    version=version,
    install_requires=[
        'odoo14-addon-base_phone',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
