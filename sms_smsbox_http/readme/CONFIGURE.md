1. In _Settings > Technical > IAP > IAP Accounts_, create an account with the _SMSBOX
   (HTTP API)_ provider, then set:
   - _SMSBOX API Key_: the API key of your SMSBOX client area;
   - _SMSBOX Mode_: _Expert_ to send with a registered _SMSBOX Sender_, _Standard_ to
     send with a short code;
   - _SMSBOX Strategy_: _Commercial_ for marketing SMS, which adds the legal STOP
     mention.
2. In _Settings > Technical > Phone / SMS > SMS Providers_, create a provider of type
   _SMSBOX (HTTP API)_ linked to this account, and move it first to use it by default.
3. Copy the _SMSBOX Delivery Reports URL_ of the account into the SMSBOX client area, in
   _My settings > My preferences > Callback URLs > Delivery reports (API)_.
