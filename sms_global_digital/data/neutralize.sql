-- Enable test mode on Global Digital SMS accounts, so that no real SMS
-- is sent on a neutralized database: they are notified in Discuss instead.
UPDATE iap_account
   SET sms_global_digital_test_mode = true
 WHERE provider = 'sms_global_digital';
