# Copyright 2014-2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# Copyright 2015-2018 Juris Malinens (port to v9)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import http


class AsteriskClick2dialController(http.Controller):
    @http.route(
        "/asterisk_click2dial/get_record_from_my_channel", type="json", auth="user"
    )
    def get_record_from_my_channel(self, **kw):
        res = http.request.env["asterisk.server"].get_record_from_my_channel()
        return res
