Automatically the system will login into the PBX server once we enter odoo with our user.
If we are on a test environment, no login is made and the libraries of SIP are not loaded.

Once we are logged, we can use the VOIP widget in order to call directly.
In order to open all the selectors, we can press the softphone button on the top bar...

.. figure:: static/description/softphone.png

...and the bottom widget will be opened.

.. figure:: static/description/widget.png

The widget can be hidden by clicking on the top bar.

.. figure:: static/description/hidden_widget.png

Clicking the top bar of the widget again will make it reappear.

We can make a call in 2 ways:

1. Clicking the partner's number in the partner view, which appears in green.
.. figure:: static/description/partner.png

2. Opening the numpad located at the bottom left of the widget, entering the desired number,
and clicking the call button located at the bottom right of the widget.
.. figure:: static/description/numpad.png

Inside a call, we can transfer the call, end the call, mute the call and put the call on Hold.

The widget offers 3 sections:

1. Recent calls: Here we have a list of the last calls made, along with additional call information such as call date and time, status, or duration.
2. Call Activities: Here we have a list of call activities assigned to us in any Odoo document(crm.lead, sale.order...) that has expired or is about to expire and needs to be completed.
3. Contacts: Lastly, we have quick access to all stored partners in our Odoo who have a telephone number set.

Clicking on any record in these three sections gives us access to the related partner, allowing us to view their information and make a call.

In the partner view of the widget, we can perform three actions:

1. Send an email to the partner.
2. Access the partner's form in Odoo.
3. Schedule an activity.

.. figure:: static/description/actions.png

If the partner is unknown and not stored in Odoo, some actions may not be available. This can occur when accessing a recent call made to a contact that is not stored for example. However, in this case, we allow the action to store the contact in Odoo from recent calls, clicking on the plus icon button.

.. figure:: static/description/unknown_partner_actions.png

Additionally, if we access a contact through the activity section, we have four more available actions:

1. Go to the related document, such as a lead or a sale.
2. Mark the activity as done.
3. Edit the activity.
4. Cancel the activity.

.. figure:: static/description/activity_actions.png

In any tab, we can perform a search by typing a keyword in the search bar, such as the contact's name or phone number.

.. figure:: static/description/search.png

Also, the system allows to receive call.
In that case, the system will try to find the related partner and will open the widget automatically.

.. figure:: static/description/received_call.png
