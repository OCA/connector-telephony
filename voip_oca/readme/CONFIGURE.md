Create the PBX Connection
-------------------------

- Access in Debug mode.
- Go to `Settings > Technical > Discuss > PBX Servers`.
- Create a PBX server and define the domain name and websocket link.

You can set it as ``Test`` or ``Production``. Test environment will never contact the PBX server.

Configure users
---------------

For each user, we need to define their PBX server, user and password if we want it to be able
to access the PBX server and make calls. To do this, we have two options:

1. Admin users can define the information directly in the user form for each user. For this,
go to Settings > Users & Companies > Users and go to VOIP tab and set the information.
2. By other hand, each user can go to Preferences and modify the information in the VOIP tab.
