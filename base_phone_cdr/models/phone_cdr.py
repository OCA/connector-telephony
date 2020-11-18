from odoo import api, models, fields


class PhoneCDR(models.Model):
    _name = 'phone.cdr'
    _description = 'Phone CDR'

    @api.depends('call_start_time', 'call_connect_time', 'inbound_flag')
    def _compute_ring_time(self):
        for rec in self:
            if rec.inbound_flag:
                rec.ring_time = rec.call_connect_time - rec.call_start_time

    @api.depends('caller_id')
    def _get_odoo_user_and_partner(self):
        for rec in self:
            if rec.inbound_flag:
                rec.user_id = self.env['res.users'].search([
                    ('related_phone', '=', rec.caller_id)], limit=1
                )
                rec.partner_id = self.env['res.partner'].search([
                    ('phone', '=', rec.caller_id)], limit=1
                )

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
    caller_id2 = fields.Char('Caller ID')
    caller_id_name2 = fields.Char('Caller ID Name')
    state = fields.Selection([('offering', 'Offering'),
                              ('connected', 'Connected'),
                              ('missed', 'Missed'),
                              ('on_hold', 'On Hold'),
                              ('completed', 'Completed')],
                              string="Status",
                              default='offering')
    user_id = fields.Many2one('res.users',
                              compute='_get_odoo_user_and_partner',
                              string='Odoo User')
    partner_id = fields.Many2one('res.partner',
                              compute='_get_odoo_user_and_partner',
                              string='Partner')
