# -*- coding: utf-8 -*-
##############################################################################
#
#    Phone Log-call module for Odoo/OpenERP
#    Copyright (C) 2016 credativ Ltd (<http://credativ.co.uk>).
#    Copyright (C) 2016 Trever L. Adams
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

from openerp import models, fields, api
import logging


logger = logging.getLogger(__name__)


class FreeSWITCHServer(models.Model):
    _inherit = "freeswitch.server"

    ucp_url = fields.Char(
        string='Script to download FreeSWITCH recordings', required=False,
        default="https://localhost/cgi-bin/get_recording.pl?file={odoo_filename}",
        help="Macros allowed: {odoo_type} (inbound, outbound), {odoo_src}"
        "(source phone number}, {odoo_dst} (destination number), "
        "{odoo_duration} (length of call), {odoo_start} (start time of call "
        "in seconds since epoch), {odoo_filename} (file name on server), "
        "{odoo_uniqueid} (FreeSWITCH UUID of call).")
    server_jitter_correction = fields.Integer(
        string='Time jitter compensation', required=True,
        help='Number of seconds to subtract from new call start and add to '
        'new call end, for call merging, to compensate for system/database '
        'load and time drift between FreeSWITCH server and Odoo/Odoo database '
        'server(s). 5 seconds is likely a good start. Above 10 seconds you get '
        'into the realm where you may have distinct calls confused. 20 - 30 '
        'seconds begins to guarantee this. It is best to keep this low '
        'and use a method to keep time synced.',
        default=5)


class PhoneCommon(models.AbstractModel):
    _inherit = 'phone.common'

    @api.model
    def _get_ucp_url(self, user):
        fs_server = user.freeswitch_server_id
        return fs_server.ucp_url

    @api.model
    def _get_jitter(self, user):
        fs_server = user.freeswitch_server_id
        return fs_server.server_jitter_correction
