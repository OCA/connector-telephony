.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=================
Base Phone Pop-up
=================

When the user receives a phone call, Odoo can automatically open the
corresponding partner/lead/employee/... in a pop-up without any action from
the user.

Installation
============

To install this module, you need to:

* Click on the module and install it

The module *web_action_request* can be downloaded with Mercurial:

hg clone http://bitbucket.org/anybox/web_action_request

It depends on 2 other modules, *web_longpolling* and *web_socketio*, that can
be downloaded with this command:

hg clone http://bitbucket.org/anybox/web_socketio

You will find some hints in this documentation :
https://bitbucket.org/anybox/web_action_request

Warning : proxying WebSockets is only supported since Nginx 1.3.13 ; the
feature provided by this module won't work with older versions of Nginx.

TODO : document this new feature on the Akretion Web site :
http://www.akretion.com/products-and-services/openerp-asterisk-voip-connector

Configuration
=============

To configure this module, you need to:

* Configure users under Settings > Users > $USER

Usage
=====

* Install, configure user, use.

Known issues / Roadmap
======================

* None

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/connector-telephony/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Contributors
------------

* Akretion
* Odoo Community Association (OCA)

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.

