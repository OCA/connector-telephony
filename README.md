[![Build Status](https://travis-ci.org/OCA/connector-telephony.svg?branch=13.0)](https://travis-ci.org/OCA/connector-telephony)
[![Coverage Status](https://coveralls.io/repos/OCA/connector-telephony/badge.png?branch=13.0)](https://coveralls.io/r/OCA/connector-telephony?branch=13.0)

# Odoo telephony connector

This projets aims at connecting Odoo to different phone systems. Phone systems currently supported are Asterisk (an OpenSource IPBX, cf [asterisk.org](http://www.asterisk.org/) and OVH (the centrex offer of OVH, cf the [OVH website](http://www.ovhtelecom.fr/telephonie/)).

This project provides:
* a serie of modules (base\_phone, base\_phone\_popup,
  crm\_phone, hr\_phone, event\_phone, etc...) that are independant from
  the phone system and can be usefull on all Odoo installations.
* several modules (asterisk\_click2dial, ovh\_telephony\_connector)
  that are specific to a particular phone system.

The main maintainer of this project is Alexis de Lattre from
Akretion (alexis.delattre \_at\_ akretion.com).

To know more about the OpenERP-Asterisk connector, refer to the documentation
 available on the Akretion website
http://www.akretion.com/en/products-and-services/openerp-asterisk-voip-connector


