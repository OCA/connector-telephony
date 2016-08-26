[![Build Status](https://travis-ci.org/OCA/connector-telephony.svg?branch=9.0)](https://travis-ci.org/OCA/connector-telephony)
[![Coverage Status](https://coveralls.io/repos/OCA/connector-telephony/badge.png?branch=9.0)](https://coveralls.io/r/OCA/connector-telephony?branch=9.0)

# Odoo telephony connector

This projets aims at connecting Odoo to different phone systems. Phone systems currently supported are Asterisk (an OpenSource IPBX, cf [asterisk.org](http://www.asterisk.org/), OVH (the centrex offer of OVH, cf the [OVH website](http://www.ovhtelecom.fr/telephonie/)) and FreeSWITCH (cross-platform multi-protocol soft switch, cf [FreeSWITCH.org](http://freeswitch.org)).

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

[//]: # (addons)

Available addons
----------------
addon | version | summary
--- | --- | ---
[asterisk_click2dial](asterisk_click2dial/) | 9.0.1.0.0 | Asterisk-Odoo connector
[base_phone](base_phone/) | 9.0.0.1.0 | Validate phone numbers
[base_phone_popup](base_phone_popup/) | 9.0.1.0.0 | Pop-up the related form view to the user on incoming calls
[crm_phone](crm_phone/) | 9.0.1.0.0 | Validate phone numbers in CRM
[event_phone](event_phone/) | 9.0.1.0.0 | Validate phone numbers in Events
[hr_phone](hr_phone/) | 9.0.1.0.0 | Validate phone numbers in HR
[hr_recruitment_phone](hr_recruitment_phone/) | 9.0.1.0.0 | Validate phone numbers in HR Recruitment


Unported addons
---------------
addon | version | summary
--- | --- | ---
[crm_claim_phone](crm_claim_phone/) | 8.0.0.1.0 (unported) | Validate phone numbers in CRM Claims
[ovh_telephony_connector](ovh_telephony_connector/) | 9.0.0.1.0 (unported) | OVH-Odoo telephony connector (click2call)

[//]: # (end addons)
