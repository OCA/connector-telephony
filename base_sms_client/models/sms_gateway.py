# coding: utf-8
# Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
# Copyright (C) 2011 SYLEAM (<http://syleam.fr/>)
# Copyright (C) 2013 Julius Network Solutions SARL <contact@julius.fr>
# Copyright (C) 2015 Valentin Chemiere <valentin.chemiere@akretion.com>
# Copyright (C) 2015 Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api

PRIORITY_LIST = [
    ('0', '0'),
    ('1', '1'),
    ('2', '2'),
    ('3', '3')
]

CLASSES_LIST = [
    ('0', 'Flash'),
    ('1', 'Phone display'),
    ('2', 'SIM'),
    ('3', 'Toolkit')
]


class SmsAbstract(models.AbstractModel):
    _name = 'sms.abstract'
    _description = 'SMS Abstract Model'

    code = fields.Char('Verification Code')
    body = fields.Text(
        string='Message',
        help="The message text that will be send along with the"
             " email which is send through this server.")
    classes = fields.Selection(
        selection=CLASSES_LIST, string='Class',
        default='1',
        help='The SMS class')
    deferred = fields.Integer(
        help='The time -in minute(s)- to wait before sending the message.')
    priority = fields.Selection(
        selection=PRIORITY_LIST, string='Priority', default='3',
        help='The priority of the message')
    coding = fields.Selection(selection=[
        ('1', '7 bit'),
        ('2', 'Unicode')
        ], string='Coding',
        help='The SMS coding: 1 for 7 bit (160 chracters max'
             'length) or 2 for unicode (70 characters max'
             'length)',
        default='1'
    )
    tag = fields.Char('Tag', help='an optional tag')
    nostop = fields.Boolean(
        default=True,
        help='Do not display STOP clause in the message, this requires that '
             'this is not an advertising message.')
    validity = fields.Integer(
        default=10,
        help="The maximum time - in minute(s) - before the message "
             "is dropped.")

    char_limit = fields.Integer(string='Character Limit', default=160)
    default_gateway = fields.Boolean()
    company_id = fields.Many2one(comodel_name='res.company', 
         default=lambda self: self.env.user.company_id)


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
