/* URL for target API. Changebthe server name, and keep the /palitto/ Odoo endpoint */
DECLARE @URL AS VARCHAR;
SELECT @URL = IF(@22='qa', 'https://QA.palittoconsulting.com/palitto/', 'http://DEVweb.palittoconsulting.com/palitto/')
/* Incoming call */
SELECT CONCAT(@URL
, 'incomingCall?Ext=', @3,
, '&amp;GuiLoginName=', GuiLoginName,
, '&amp;CallID=', @25,
, '&amp;GUID=', @27,
, '&amp;TapiID=', @14,
, '&amp;CallerID=', @17,
, '&amp;CalledID=', @19,
, '&amp;External=', @15,
, '&amp;Inbound=', @16,
, '&amp;StartTime=', @23,
, '&amp;Auth=', sha1(CONCAT('MySecretKey', GuiLoginName)),
, '&amp;Math=', RAND()) AS EventTriggerCommand
FROM users WHERE UserDN = @3 AND @4 = 'Offering' AND @16 = '1'
/* Outgoing call */
UNION SELECT CONCAT(@URL
, 'outgoingCall?Ext=', @3,
, '&amp;GuiLoginName=', GuiLoginName,
, '&amp;CallID=', @25,
, '&amp;GUID=', @27,
, '&amp;TapiID=', @14,
, '&amp;CallerID=', @17,
, '&amp;CalledID=', @19,
, '&amp;External=', @15
, '&amp;Inbound=', @16,
, '&amp;StartTime=', @23
, '&amp;Auth=', sha1(CONCAT('MySecretKey', GuiLoginName)),
, '&amp;Math=', RAND()) AS EventTriggerCommand
FROM usersWHERE UserDN = @3 AND @4 = 'Connected' AND @16 = '0' AND @24 = '0'
/* Missed call */
UNION SELECT CONCAT(@URL
, 'missedCall?Ext=', @3,
, '&amp;GuiLoginName=', GuiLoginName,
, '&amp;CallID=', @25,
, '&amp;GUID=', @27,
, '&amp;TapiID=', @14,
, '&amp;CallerID=', @17,
, '&amp;CalledID=', @19,
, '&amp;External=', @15
, '&amp;Inbound=', @16,
, '&amp;StartTime=', @23,
, '&amp;EndTime=', NOW(),
, '&amp;Auth=', sha1(CONCAT('MySecretKey', GuiLoginName)),
, '&amp;Math=', RAND()) AS EventTriggerCommand
FROM users WHERE UserDN = @3 AND @4 = 'Disconnected' AND @16 = '1' AND @21 = ''
/* Call answered */
UNION SELECT CONCAT(@URL
, 'answeredCall?Ext=', @3,
, '&amp;GuiLoginName=', GuiLoginName,
, '&amp;CallID=', @25,
, '&amp;GUID=', @27,
, '&amp;TapiID=', @14,
, '&amp;CallerID=', @17,
, '&amp;CalledID=', @19,
, '&amp;External=', @15
, '&amp;Inbound=', @16,
, '&amp;StartTime=', @23,
, '&amp;Auth=', sha1(CONCAT('MySecretKey', GuiLoginName)),
, '&amp;Math=', RAND()) AS EventTriggerCommand
FROM users WHERE UserDN = @3 AND @4 = 'Connected' AND @16 = '1' AND @24 = '0'
/* Call completed */
UNION SELECT CONCAT(@URL
, 'callCompleted?Ext=', @3,
, '&amp;GuiLoginName=', GuiLoginName,
, '&amp;CallID=', @25,
, '&amp;GUID=', @27,
, '&amp;TapiID=', @14,
, '&amp;CallerID=', @17,
, '&amp;CalledID=', @19,
, '&amp;External=', IF(@11='', '0', '1'),
, '&amp;Inbound=', @16,
, '&amp;StartTime=', @23,
, '&amp;EndTime=', NOW(),
, '&amp;Duration=', TIME_TO_SEC(TIMEDIFF(NOW(), @21)),
, '&amp;TotalDuration=', TIME_TO_SEC(TIMEDIFF(NOW(), @23)),
, '&amp;Auth=', sha1(CONCAT('MySecretKey', GuiLoginName)),
, '&amp;Math=', RAND()) AS EventTriggerCommand
FROM users WHERE UserDN = @3 AND @4 = 'Idle' AND @21 &lt;&gt; '' AND @28 = ''
/* Held Call */
UNION SELECT CONCAT(@URL
, 'heldCall?Ext=', @3,
, '&amp;GuiLoginName=', GuiLoginName,
, '&amp;CallID=', @25,
, '&amp;GUID=', @27,
, '&amp;TapiID=', @14,
, '&amp;CallerID=', @17,
, '&amp;CalledID=', @19,
, '&amp;External=', @15
, '&amp;Inbound=', @16,
, '&amp;StartTime=', @23,
, '&amp;Auth=', sha1(CONCAT('MySecretKey', GuiLoginName)),
, '&amp;Math=', RAND()) AS EventTriggerCommand
FROM users WHERE UserDN = @3 AND (@4 = 'Onhold' OR @4 = 'OnholdPendConf' OR @4 = 'OnholdPendTransf')
/* Unheld Call */
UNION SELECT CONCAT(@URL
, 'unheldCall?Ext=', @3,
, '&amp;GuiLoginName=', GuiLoginName,
, '&amp;CallID=', @25,
, '&amp;GUID=', @27,
, '&amp;TapiID=', @14,
, '&amp;CallerID=', @17,
, '&amp;CalledID=', @19,
, '&amp;External=', @15
, '&amp;Inbound=', @16,
, '&amp;StartTime=', @23,
, '&amp;Auth=', sha1(CONCAT('MySecretKey', GuiLoginName)),
, '&amp;Math=', RAND()) AS EventTriggerCommand
FROM users WHERE UserDN = @3 AND @4 = 'Connected' AND @24 = '1'
/* Conferenced Call */
UNION SELECT CONCAT(@URL
, 'unheldCall?Ext=', @3,https://10.98.97.225
, '&amp;GuiLoginName=', GuiLoginName,
, '&amp;CallID=', @25,
, '&amp;GUID=', @27,
, '&amp;TapiID=', @14,
, '&amp;CallerID=', @17,
, '&amp;CalledID=', @19,
, '&amp;External=', @15
, '&amp;Inbound=', @16,
, '&amp;StartTime=', @23,
, '&amp;Auth=', sha1(CONCAT('MySecretKey', GuiLoginName)),
, '&amp;Math=', RAND()) AS EventTriggerCommand
FROM users WHERE UserDN = @3 AND @4 = 'tcsConferenced'
