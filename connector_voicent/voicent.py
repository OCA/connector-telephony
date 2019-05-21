# Copyright (C) 2018 Voicent
# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#
# Documentation available at https://voicent.com/developer/docs/camp-api/

import ntpath
import requests
import ast


class Voicent():

    def __init__(self, host="localhost", port="8155"):
        self.host_ = host
        self.port_ = port

    def postToGateway(self, urlstr, params, files=None):
        url = "http://" + self.host_ + ":" + self.port_ + urlstr
        res = requests.post(url, params, files=files)
        return res.text

    def getReqId(self, rcstr):
        index1 = rcstr.find("[ReqId=")
        if (index1 == -1):
            return ""
        index1 += 7
        index2 = rcstr.find("]", index1)
        if (index2 == -1):
            return ""
        return rcstr[index1:index2]

    def callText(self, phoneno, text, selfdelete):
        urlstr = "/ocall/callreqHandler.jsp"
        params = {
            'info': 'simple text call',
            'phoneno': phoneno,
            'firstocc': 10,
            'txt': text,
            'selfdelete': selfdelete
        }
        res = self.postToGateway(urlstr, params)
        return self.getReqId(res)

    def callAudio(self, phoneno, filename, selfdelete):
        urlstr = "/ocall/callreqHandler.jsp"
        params = {
            'info': 'simple audio call',
            'phoneno': phoneno,
            'firstocc': 10,
            'audiofile': filename,
            'selfdelete': selfdelete
        }
        res = self.postToGateway(urlstr, params)
        return self.getReqId(res)

    def callIvr(self, phoneno, appname, selfdelete):
        urlstr = "/ocall/callreqHandler.jsp"
        params = {
            'info': 'simple text call',
            'phoneno': phoneno,
            'firstocc': 10,
            'startapp': appname,
            'selfdelete': selfdelete
        }
        res = self.postToGateway(urlstr, params)
        return self.getReqId(res)

    def callStatus(self, reqid):
        urlstr = "/ocall/callstatusHandler.jsp"
        params = {'reqid': reqid}
        res = self.postToGateway(urlstr, params)
        return self.getReqId(res)

    def callRemove(self, reqId):
        urlstr = "/ocall/callremoveHandler.jsp"
        params = {'reqid': reqId}
        res = self.postToGateway(urlstr, params)
        return self.getReqId(res)

    def callTillConfirm(self, vcastexe, vocfile, wavfile, ccode):
        urlstr = "/ocall/callreqHandler.jsp"
        cmdline = "\""
        cmdline += vocfile
        cmdline += "\""
        cmdline += " -startnow"
        cmdline += " -confirmcode "
        cmdline += ccode
        cmdline += " -wavfile "
        cmdline += "\""
        cmdline += wavfile
        cmdline += "\""

        params = {
            'info': 'Simple Call till Confirm',
            'phoneno': '1111111',
            'firstocc': 10,
            'selfdelete': 0,
            'startexec': vcastexe,
            'cmdline': cmdline
        }
        res = self.postToGateway(urlstr, params)
        return self.getReqId(res)

    ################
    # CAMPAIGN API #
    ################

    def importCampaign(self, listname, filepath):
        urlstr = "/ocall/campapi"
        params = {
            'action': 'import',
            'importfile': ntpath.basename(filepath),
            'importfilepath': filepath,
            'profile': 'Test',
            'mod': 'cus',
            'fieldsep': ',',
            'row1': 1,
            'mergeopt': 'empty',
            'leadsrcname': listname
        }
        files = {
            'file': (ntpath.basename(filepath), open(filepath, 'rb'))
        }
        res = self.postToGateway(urlstr, params, files)
        return ast.literal_eval(res)

    def runCampaign(self, listname):
        urlstr = "/ocall/campapi"
        params = {
            'action': 'bbp',
            'CAMP_NAME': 'Test',
            'listname': listname,
            'phonecols': 'Phone',
            'lines': '4',
            'calldisps': '',
            'callerid': '+18884728568',
        }
        res = self.postToGateway(urlstr, params)
        return ast.literal_eval(res)

    def importAndRunCampaign(self, filepath, msgtype, msginfo):
        urlstr = "/ocall/campapi"
        params = {
            'action': 'bbp',
            # Parameters for importing the campaign
            'importfile': ntpath.basename(filepath),
            'importfilepath': filepath,
            #'profile': 'Test',
            'mod': 'cus',
            'row1': 1,
            'leadsrcname': 'Test',
            # Parameters for running the campaign
            'CAMP_NAME': 'Test',
            'phonecols': 'Phone',
            'lines': '4',
            'calldisps': '',
            'callerid': '+18884728568',
            # Parameters for Autodialer
            'msgtype': msgtype,
            'msginfo': msginfo,
        }
        files = {
            'file': (ntpath.basename(filepath), open(filepath, 'rb'))
        }
        res = self.postToGateway(urlstr, params, files)
        return ast.literal_eval(res)

    def checkStatus(self, leadsrc_id):
        urlstr = "/ocall/campapi"
        params = {
            'action': 'campstats',
            'leadsrc_id': leadsrc_id
        }
        res = self.postToGateway(urlstr, params)
        return ast.literal_eval(res)

    def exportResult(self, camp_id, filename, extracols):
        urlstr = "/ocall/campapi"
        params = {
            'action': 'exportcamp',
            'camp_id_id': camp_id,
            'f': filename,
            'extracols': extracols
        }
        res = self.postToGateway(urlstr, params)
        return ast.literal_eval(res)
