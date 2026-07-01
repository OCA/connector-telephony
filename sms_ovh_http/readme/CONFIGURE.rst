To configure this module, you need to:

* Go to Settings > Technical > IAP Account
* Create a new account with **SMS OVH HTTP** as provider
* Fill in your OVH API credentials:

  * **Application Key**: your OVH application key
  * **Application Secret**: your OVH application secret
  * **Consumer Key**: your OVH consumer key
  * **Service Name**: your OVH SMS service name (e.g. ``sms-ab1234-1``)
  * **Sender Name**: the sender name displayed on the SMS

* You can now send an SMS!

To generate your OVH API credentials, visit https://api.ovh.com/createToken/ and
request ``POST /sms/{serviceName}/jobs`` permission.
