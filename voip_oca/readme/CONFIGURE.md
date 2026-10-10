Create the PBX Connection
-------------------------

- Access in Debug mode.
- Go to `Settings > Technical > Discuss > PBX Servers`.
- Create a PBX server and define the domain name and websocket link.    

You can set it as ``Test`` or ``Production``. Test environment will never contact the PBX server.

Asterisk Configuration
----------------------

- Go to your FreePBX
- Set up your extension to [accept websocket protocol](https://docs.asterisk.org/Configuration/WebRTC/Configuring-Asterisk-for-WebRTC-Clients/) 
- In Odoo, the TLS secured web socket link has this pattern : 
        `wss://[your_ipbx.fqdn][:websocket_listening_port]/ws`



Configure users
---------------

For each user, we need to define their PBX server, user and password if we want it to be able
to access the PBX server and make calls. To do this, we have two options:

1. Admin users can define the information directly in the user form for each user. For this,
go to Settings > Users & Companies > Users and go to VOIP tab and set the information.
2. By other hand, each user can go to Preferences and modify the information in the VOIP tab.
