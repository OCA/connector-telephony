Phone Log-call
=================

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
