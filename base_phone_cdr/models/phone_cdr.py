# -*- coding: utf-8 -*-

from odoo import api, models, fields, _
from odoo.addons.web.controllers.main import clean_action
import logging
logger = logging.getLogger(__name__)


class PhoneCDR(models.Model):
    _name = 'phone.cdr'
    _description = 'Phone CDR'

    @api.depends('call_start_time', 'call_connect_time', 'inbound_flag')
    def _compute_ring_time(self):
        for rec in self:
            if rec.inbound_flag:
                rec.ring_time = rec.call_connect_time - rec.call_start_time

    guid = fields.Char('Call GUID')
    inbound_flag = fields.Selection([('outbound', 'Outbound'),
                                     ('inbound', 'Inbound')],
                                     string='Call Inbound flag')
    call_start_time = fields.Datetime('Call start time')
    call_connect_time = fields.Datetime('Call connect time')
    ring_time = fields.Datetime(compute="_compute_ring_time",
                            string='Compute ring time')
    caller_id = fields.Char('Caller ID')
    caller_id_name = fields.Char('Caller ID Name')
