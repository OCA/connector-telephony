This module doesn't do anything on its own, it is meant to be used by developers to implement SMS providers.

To add a SMS provider, create an Python Class that implements SmsApiBase
from connector-telephony/sms_alternative_provider/models/sms_api.py.

Required implementations:
- variable KEY
- variable NAME
- function _send_sms_batch

Optional implementations:
- variable DESCRIPTION
- function _get_sms_api_error_messages

Probably your provider needs some api key or similar to function, add those fields prefixed with your gateway\_type name to the gateway class:

    your_sms_provider_apikey = fields.Char('API key')

and add a group after group ``general`` in the form view of the model:

    <group name="general" position="after">
        <group name="your_sms_provider" attrs="{'invisible': [('gateway_type', '!=', 'your_sms_provider')]}">
            <field name="your_sms_provider_apikey" password="True" attrs="{'required': [('gateway_type', '=', 'your_sms_provider')]}" />
        </group>
    </group>
