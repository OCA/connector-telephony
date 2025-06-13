This module allows the use of VOIP directly from Odoo.

It relies on SIP.js to connect to the PBX using a websocket directly from the browser.

Odoo server will not connect directly to the PBX server, but will have users and passwords stored.

In order to use this module, you need to have a PBX server that allows websocket connection.
Otherwise, you need to use a proxy that will be the bridge between Odoo and PBX.
Websocket connection is required because browsers prefer this kind of connections.
Also, this is an standard connection defined on RFC 7118 by IETF.
Several PBX servers support this protocol.
