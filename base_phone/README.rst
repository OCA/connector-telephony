.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==========
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

* *phone* : should be True for a phone number, False (default) otherwize.
* *phone_format* : it can have 3 possible values :
    * *international* (default) : the report will display '+33 1 55 42 12 42'
    * *national* : the report will display '01 55 42 12 42'
    * *e164* : the report will display '+33155421242'

For example, in the Sale Order report, to display the phone number of the
Salesman, you can write :  o.user_id and o.user_id.phone and
format(o.user_id.phone, phone=True, phone_format='national') or ''

This module is independant from the Asterisk connector.

Please contact Alexis de Lattre from Akretion <alexis.delattre@akretion.com>
for any help or question about this module.

Installation
============

There is no specific installation procedure for this module.

Configuration
=============

There is no specific configuration procedure for this module.

Usage
=====

There is no specific usage procedure for this module.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/{repo_id}/9.0

Known issues / Roadmap
======================


Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/{project_repo}/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed `feedback
<https://github.com/OCA/connector-telephony/issues/new?body=module:%20base_phone%0Aversion:%209.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Alexis de Lattre <alexis.delattre@akretion.com>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
