-- disable VOIP module by default

UPDATE voip_pbx SET mode = 'test';
UPDATE res_users SET voip_username = NULL, voip_password = NULL WHERE voip_username IS NOT NULL;
