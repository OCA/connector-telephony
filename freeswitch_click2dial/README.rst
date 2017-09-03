.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=====================
FreeSWITCH Click2Dial
=====================

The technical name of this module is *freeswitch_click2dial*, but this module
implements much more than a simple *click2dial* ! This module adds 3
functionalities:

1) It adds a *Dial* button in the partner form view so that users can directly
   dial a phone number through FreeSWITCH. This feature is usually known as
   *click2dial*. Here is how it works :

    * In OpenERP, the user clicks on the *Dial* button next to a phone number
      field in the partner view.

    * OpenERP connects to the FreeSWITCH Event Socket and FreeSWITCH makes the
      user's phone ring.

    * The user answers his own phone (if he doesn't, the process stops here).

    * FreeSWITCH dials the phone number found in OpenERP in place of the user.

    * If the remote party answers, the user can talk to his correspondent.

2) It adds the ability to show the name of the calling party on the screen of
   your IP phone on incoming phone calls if the presented phone number is
   present in the partner/leads/employees/... of OpenERP. To understand how to
   use this, please see get_caller_name.py, which should be installed per the
   instructions in the script on the OpenERP/Odoo server. This works for
   incoming and outgoing calls, per instructions in the script.

3) It adds a phone icon (*Open Caller*) in the top menu bar
   (next to the Preferences) to get the partner/lead/candidate/registrations
   corresponding to the calling party in one click. Here is how it works :

    * When the user clicks on the phone icon, OpenERP sends a query to the
      FreeSWITCH Manager Interface to get a list of the current phone calls

    * If it finds a phone call involving the user's phone, it gets the phone
      number of the calling party

    * It searches the phone number of the calling party in the
      Partners/Leads/Candidates/Registrations of OpenERP. If a record matches,
      it takes you to the form view of this record. If no record matchs, it
      opens a wizard which proposes to create a new Partner with the presented
      phone number as *Phone* or *Mobile* number or update an existing Partner.

    It is possible to get a pop-up of the record corresponding to the calling
    party without any action from the user via the module *base_phone_popup*.

Installation
============

To install this module, you need to:

* Click on the module and install it

Additionally, you will need the FreeSWITCH ESL python module. The easiest way is
pip install FreeSWITCH-ESL-Python. Otherwise, you will find it under
${FREESWITCH_SRC_TOP_DIR}/libs/esl/python. Go to
${FREESWITCH_SRC_TOP_DIR}/libs/esl. Type make. Then make pymod. You will then
need to install ${FREESWITCH_SRC_TOP_DIR}/libs/esl/python/ESL.py and
${FREESWITCH_SRC_TOP_DIR}/libs/esl/python/_ESL.so into the appropriate places
on your OpenERP/Odoo server.
(https://wiki.freeswitch.org/wiki/Event_Socket_Library#Installation for more
information.) An alternative method would involve
https://github.com/gurteshwar/freeswitch-esl-python.

Configuration
=============

To configure this module, you need to:

* Settings > Technical > FreeSWITCH Servers
* Setup you server
* Configure users under Settings > Users > $USER > Telphony tab

Usage
=====

To use this module, you need to:

* See scripts/get_caller_name.py to see how to set caller and callee name

* Click on Dial next to any phone number covered by associated modules

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/{repo_id}/{branch}

.. repo_id is available in https://github.com/OCA/maintainer-tools/blob/master/tools/repos_with_ids.txt
.. branch is "8.0" for example

Known issues / Roadmap
======================

* None

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/
{project_repo}/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback `here <https://github.com/OCA/
{project_repo}/issues/new?body=module:%20
{module_name}%0Aversion:%20
{version}%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.


Credits
=======

Contributors
------------

* Firstname Lastname <email.address@example.org>
* Second Person <second.person@example.org>

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

