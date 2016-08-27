# -*- coding: utf-8 -*-
# (c) 2014 Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import openerp


class FreeSWITCHClick2dialController(openerp.addons.web.http.Controller):
    _cp_path = '/freeswitch_click2dial'

    @openerp.addons.web.http.jsonrequest
    def get_record_from_my_channel(self, req):
        FreeswitchServer = req.session.model('freeswitch.server')
        return FreeswitchServer.get_record_from_my_channel()
