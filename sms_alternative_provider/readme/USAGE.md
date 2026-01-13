This module doesn't do anything on its own, it is meant to be used by developers to implement SMS providers.

To do this, it suffices to inherit the ``ir.sms.gateway`` model to add a type:

    gateway_type = fields.Selection(selection_add=[("your_sms_provider", "Your SMS provider")])

and declare a function named like \_send_$type:

    def _send_your_sms_provider(self, messages):
        # do here whatever you need to send the list of messages:
        # [{
        #    'id': id of the sms.sms record (may not be set),
        #    'number': the number to send the sms to
        #    'content': the content of the message
        # }]
        # return a list of dicts with sending results:
        # [{
        #    'id': id of the sms.sms record
        #    'state': sms.sms#state
        #    'failure_type': sms.sms#failure_type if state == 'error'
        #    # whatever other fields you want to write on the sms.sms record after sending,
        #    # such as provider-specific extra information
        # }]

Probably your provider needs some api key or similar to function, add those fields prefixed with your gateway\_type name to the gateway class:

    your_sms_provider_apikey = fields.Char('API key')

and add a group after group ``general`` in the form view of the model:

    <group name="general" position="after">
        <group name="your_sms_provider" attrs="{'invisible': [('gateway_type', '!=', 'your_sms_provider')]}">
            <field name="your_sms_provider_apikey" password="True" attrs="{'required': [('gateway_type', '=', 'your_sms_provider')]}" />
        </group>
    </group>
