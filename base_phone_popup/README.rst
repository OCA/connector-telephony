.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

Base Phone Pop-up
=================

When the user receives a phone call, OpenERP can automatically open the
corresponding partner/lead/employee/... in a pop-up without any action from the
user.

Installation
============

The module requires:
* web_action_request
* web_socketio
* web_longpolling

Usage
=====

You will find some hints in this documentation :
https://bitbucket.org/anybox/web_action_request


TODO : document this new feature on the Akretion Web site :
http://www.akretion.com/products-and-services/openerp-asterisk-voip-connector

For further information, please visit:

* https://www.odoo.com/forum/help-1

Known issues / Roadmap
======================

Warning : proxying WebSockets is only supported since Nginx 1.3.13 ; the
feature provided by this module won't work with older versions of Nginx.

Credits
=======

Contributors
------------

* Alexis de Lattre <alexis.delattre@akretion.com>
* Sandy Carter <sandy.carter@savoirfairelinux.com>
* Matjaz Mozetic <info@matmoz.si>
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
