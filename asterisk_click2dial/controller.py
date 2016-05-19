# -*- coding: utf-8 -*-
# © 2014-2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import openerp


class AsteriskClick2dialController(openerp.addons.web.http.Controller):
    _cp_path = '/asterisk_click2dial'

    @openerp.addons.web.http.jsonrequest
    def get_record_from_my_channel(self, req):
        res = req.session.model('asterisk.server').get_record_from_my_channel()
        return res
