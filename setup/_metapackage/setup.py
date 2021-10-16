import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo13-addons-oca-connector-telephony",
    description="Meta package for oca-connector-telephony Odoo addons",
    version=version,
    install_requires=[
        'odoo13-addon-base_phone',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 13.0',
    ]
)
