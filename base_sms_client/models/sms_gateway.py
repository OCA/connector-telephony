# Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
# Copyright (C) 2011 SYLEAM (<http://syleam.fr/>)
# Copyright (C) 2013 Julius Network Solutions SARL <contact@julius.fr>
# Copyright (C) 2015 Valentin Chemiere <valentin.chemiere@akretion.com>
# Copyright (C) 2015 Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class SmsGateway(models.Model):
    _name = 'sms.gateway'
    _description = 'SMS Client'
    _inherit = 'sms.abstract'

    name = fields.Char(string='Gateway Name', required=True)
    from_provider = fields.Char(string="From")
    method = fields.Selection(string='API Method', selection=[])
    url = fields.Char(
        string='Gateway URL', help='Base url for message')
    state = fields.Selection(selection=[
        ('new', 'Not Verified'),
        ('waiting', 'Waiting for Verification'),
        ('confirm', 'Verified'),
        ], string='Gateway Status', index=True, readonly=True, default='new')
    user_ids = fields.Many2many(
        comodel_name='res.users',
        string='Users Allowed to use the gateway')

    @api.multi
    def _check_permissions(self):
        self.ensure_one()
        if self.env.uid not in self.sudo().user_ids.ids:
            return False
        return True

    @api.model
    def _run_send_sms(self, domain=None):
        if domain is None:
            domain = []
        domain.append(('state', '=', 'draft'))
        sms = self.env['sms.sms'].search(domain)
        return sms.send()
