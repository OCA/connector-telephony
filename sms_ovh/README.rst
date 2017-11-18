.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

===============
SMS client OVH
===============

This module provide OVH fields to create OVH gateway.

Usage
=====

* Create your application on this page : https://eu.api.ovh.com/createApp/
* Buy Sms package on https://www.ovh.com/
* Excecute this script to get your consumer key and set the access right settings::

   # -*- encoding: utf-8 -*-

   import ovh

   # Put your application key
   application_key='your_application_key'

   # Put your application secret
   application_secret='your_application_secret'

   # Put your endpoint default = 'ovh-eu'
   endpoint = 'ovh-eu'

   # create a client using configuration
   client = ovh.Client(endpoint, application_key=application_key, application_secret=application_secret, consumer_key='' )

   # Request RO, /me API access
   ck = client.new_consumer_key_request()
   ck.add_rules(ovh.API_READ_ONLY, "/me")

   # Request token
   validation = ck.request()

   print "Please visit %s to authenticate, and come back here." % validation['validationUrl']
   raw_input("and press Enter to continue...")

   # Print your consumer Key
   print "Welcome", client.get('/me')['firstname']
   print "Btw, your 'consumerKey' is '%s'" % validation['consumerKey']

   # Request RW, /me and /sms API access
   ck.add_recursive_rules(ovh.API_READ_ONLY, "/me")
   ck.add_recursive_rules(ovh.API_READ_WRITE, "/sms")

   raw_input("and press Enter to close...")

* go to settings > technical > Sms Provider configuration and select OVH in provider.


Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/ovh_sms_client/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback

Credits
=======

Contributors
------------

* Valentin Chemiere
* Yvan Party <yvan@julius.fr>
* MonsieurB <monsieurb@saaslys.com>

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
