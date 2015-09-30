# -*- coding: utf-8 -*-
##############################################################################
#
#    FreeSWITCH click2dial module for OpenERP
#    Copyright (C) 2014 Alexis de Lattre (alexis@via.ecp.fr)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import openerp


class FreeSWITCHClick2dialController(openerp.addons.web.http.Controller):
    _cp_path = '/freeswitch_click2dial'

    @openerp.addons.web.http.jsonrequest
    def get_record_from_my_channel(self, req):
        res = req.session.model('freeswitch.server').get_record_from_my_channel()
        return res
