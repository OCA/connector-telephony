# -*- coding: utf-8 -*-
# (c) 2016 credativ Ltd (<http://credativ.co.uk>).
# (c) 2016 Trever L. Adams
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

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
