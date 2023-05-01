This module provides common methods and wizards which can be useful to
develop a connector between Odoo and a telephony system. It depends on
the official module *phone_validation* which handle the reformatting of
phone numbers using the
[phonenumbers](https://github.com/daviddrysdale/python-phonenumbers)
Python library, which is a port of the library used in Android
smartphones. For example, if your user is linked to a French company and
you update the form view of a partner with a badly written French phone
number such as '01-55-42-12-42', Odoo will automatically update the
phone number to [E.164](https://en.wikipedia.org/wiki/E.164) format
'+33155421242'. This module extends this reformatting to create() and
write() methods.

This module is used by the Odoo-Asterisk connector of the OCA.
