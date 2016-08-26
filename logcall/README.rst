.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

========
Log-call
========

When a call has completed within Asterisk, FreeSWITCH or similar
a callback can be added in a hangup handler to call a script
which sends a request to Odoo to log the call.

This module requires a module providing _get_ucp_url and _get_jitter
functions in PhoneCommon. These provide a URL template for downloading
recordings (false is fine) and the number of seconds to use to make
sure there are no problems in merging call logs, respectively.

Merging of call logs is automatic if, and only if, the call existing in
the database as a state time between the start of the new call minus jitter
and end of the new call plus jitter. It keep the data making the call the
longest. It will keep the original attachment, ignoring a new one. It will
append the new call description to the old making sure that the old ends with
a new line.

Installation
============

To install this module, you need to simply click install.

Configuration
=============

To configure this module, you need to go to the configuration page for the
FreeSWITCH server in question, within Odoo, make sure to edit the ucp_url
field to be a url template for call recordings.

The following macros are allowed:
{odoo_type} (inbound, outbound)
{odoo_src} (source phone number}
{odoo_dst} (destination number)
{odoo_duration} (length of call)
{odoo_start} (start time of call in seconds since epoch)
{odoo_filename} (file name on server)
{odoo_uniqueid} (FreeSWITCH UUID of call)

Make sure to set time jitter compensation which is the number of seconds to
subtract from new call start and add to new call end, for call merging, to
compensate for system/database load and time drift between FreeSWITCH server
and Odoo/Odoo database server(s). 5 seconds is likely a good start. Above 10
seconds you get into the realm where you may have distinct calls confused.
20 - 30 seconds begins to guarantee this. It is best to keep this low and use
a method to keep time synced.

Usage
=====

To use this module, you will need to use one of the scripts in logcall/scripts
which is appropriate for your server. You will also need Asterisk Logcall,
FreeSWITCH Logcall, or something similar to provide ucp_url and
server_jitter_compensation. Configure those.

Note: the scripts, properly used, will work in most situations. Adjust for your
local conditions. Please, contribute useful changes.

For users who wish to enable automatic call logging, they will need to set the
"Automatically Log Incoming Calls" preference.

The user that will be handling to call backs should have "Phone System
Integration and Logging" checked. It probably should be the same user you use
for caller pop-up and Caller ID notification from other modules in
connector-telephony. It should have no other permissions or group memberships
besides what is set by those mentioned here.

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
* Ondřej Kuzník <ondrej.kuznik@credativ.co.uk>

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
