.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

Base Phone
==========

This module validate phone numbers using the *phonenumbers* Python library,
which is a port of the library used in Android smartphones. For example, if
your user is linked to a French company and you update the form view of a
partner with a badly written French phone number such as '01-55-42-12-42',
Odoo will automatically update the phone number to E.164 format '+33155421242'
and display in the form and tree view of the partner the readable equivalent
'+33 1 55 42 12 42'.

This module also adds *tel:* links on phone numbers and *fax:* links on fax
numbers. If you have a softphone or a client software on your PC that is
associated with *tel:* links, the softphone should propose you to dial the
phone number when you click on such a link.

This module also updates the format() function for reports and adds 2
arguments :

* *phone* : should be True for a phone number, False (default) otherwise.
* *phone_format* : it can have 3 possible values :
    * *international* (default) : the report will display '+33 1 55 42 12 42'
    * *national* : the report will display '01 55 42 12 42'
    * *e164* : the report will display '+33155421242'

For example, in the Sale Order report, to display the phone number of the
Salesman, you can write :  o.user_id and o.user_id.phone and
format(o.user_id.phone, phone=True, phone_format='national') or ''

This module is independent from the Asterisk connector.

Installation
============

To install this module, you need to:

* to install phonenumbers: pip install phonenumbers

Usage
=====

For further information, please visit:

* https://www.odoo.com/forum/help-1

Credits
=======

Contributors
------------

* Alexis de Lattre <alexis.delattre@akretion.com>
* Jordi Riera <kender.jr@gmail.com>

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
