.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=======================
CRM VoIP Phone Log-call
=======================

This bridge  in a configuration option for use by logcall. This enables linking
to call recordings in the logcall functionality.

Installation
============

To install this module, you need to simply click install.

Configuration
=============

To configure this module, you need to go to the configuration page for the
CRM Voip module, within Odoo, make sure to edit the ucp_url field to be a url
template for call recordings.

The following macros are allowed:
{odoo_type} (inbound, outbound)
{odoo_src} (source phone number)
{odoo_dst} (destination number)
{odoo_duration} (length of call)
{odoo_start} (start time of call in seconds since epoch)
{odoo_filename} (file name on server)
{odoo_uniqueid} (Asterisk UUID of call)

Make sure to set time jitter compensation which is the number of seconds to
subtract from new call start and add to new call end, for call merging, to
compensate for system/database load and time drift between Asterisk server
and Odoo/Odoo database server(s). 5 seconds is likely a good start. Above 10
seconds you get into the realm where you may have distinct calls confused.
20 - 30 seconds begins to guarantee this. It is best to keep this low and use
a method to keep time synced.

Known issues / Roadmap
======================

None at this time.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/connector-telephony/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Trever L. Adams <trever.adams@gmail.com>

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
