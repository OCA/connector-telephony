# -*- coding: utf-8 -*-
# © 2014-2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# © 2015-2016 Juris Malinens (port to v9)
# © 2014-2016 Trever Adams
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import http


class FreeSWITCHClick2dialController(http.Controller):
    _cp_path = '/freeswitch_click2dial'

    @http.route(
        '/freeswitch_click2dial/get_record_from_my_channel/',
        type='json', auth='public')
    def get_record_from_my_channel(self, **kw):
        res = http.request.env['freeswitch.server'].get_record_from_my_channel()
        return res
