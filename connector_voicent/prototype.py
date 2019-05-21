# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


# Simple message
import voicent
v = voicent.Voicent()
phoneno = "6024275632"
reqid = v.callText(phoneno, "Hello, This is a test of the autodialer.", "1")
status = v.callStatus(reqid)

# Using Campaign in 2 steps
import voicent
v = voicent.Voicent()
filepath = "/home/mchambreuil/odoo/pvm/voicent.csv"
listname = "Test"
leadsrc_id = v.importCampaign(listname, filepath)
res = v.runCampaign(listname)
v.checkStatus(res['leadsrc_id'])

# Using Campaign in 1 step with TTS
import voicent
v = voicent.Voicent()
filepath = "/home/mchambreuil/odoo/pvm/voicent.csv"
res = v.importAndRunCampaign(filepath, "tts", "Hello, This is a test. Bye")
status = v.checkStatus(res['camp_id'])

# Using Campaign in 1 step with Template
import voicent
v = voicent.Voicent()
filepath = "/home/mchambreuil/odoo/pvm/voicent.csv"
res = v.importAndRunCampaign(filepath, "template", "Test")
status = v.checkStatus(res['camp_id'])
