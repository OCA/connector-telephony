# coding: utf-8
# Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
# Copyright (C) 2011 SYLEAM (<http://syleam.fr/>)
# Copyright (C) 2013 Julius Network Solutions SARL <contact@julius.fr>
# Copyright (C) 2015 Valentin Chemiere <valentin.chemiere@akretion.com>
# Copyright (C) 2015 Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

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


class SMSClient(models.Model):
    _name = 'sms.gateway'
    _description = 'SMS Client'

    @api.model
    def get_method(self):
        return []

    name = fields.Char(string='Gateway Name', required=True)
    from_provider = fields.Char(string="From")
    method = fields.Selection(
        string='API Method',
        selection='get_method')
    url = fields.Char(
        string='Gateway URL', help='Base url for message')
    state = fields.Selection(selection=[
        ('new', 'Not Verified'),
        ('waiting', 'Waiting for Verification'),
        ('confirm', 'Verified'),
        ], string='Gateway Status', index=True, readonly=True, default='new')
    user_ids = fields.Many2many(
        comodel_name='res.users',
        string='Users Allowed')
    code = fields.Char('Verification Code')
    body = fields.Text(
        string='Message',
        help="The message text that will be send along with the"
             " email which is send through this server.")
    validity = fields.Integer(
        default=10,
        help="The maximum time - in minute(s) - before the message "
             "is dropped.")
    classes = fields.Selection(
        selection=CLASSES_LIST, string='Class',
        default='1',
        help='The SMS class: flash(0),phone display(1),SIM(2),toolkit(3)')
    deferred = fields.Integer(
        default=0,
        help='The time -in minute(s)- to wait before sending the message.')
    deferred_visible = fields.Boolean(default=False)
    priority = fields.Selection(
        selection=PRIORITY_LIST, string='Priority', default='3',
        help='The priority of the message')
    coding = fields.Selection(selection=[
        ('1', '7 bit'),
        ('2', 'Unicode')
        ], string='Coding',
        help='The SMS coding: 1 for 7 bit (160 chracters max'
             'lenght) or 2 for unicode (70 characters max'
             'lenght)',
        default='1'
    )
    tag = fields.Char('Tag', help='an optional tag')
    nostop = fields.Boolean(
        default=True,
        help='Do not display STOP clause in the message, this requires that '
             'this is not an advertising message.')
    char_limit = fields.Boolean('Character Limit', default=True)
    default_gateway = fields.Boolean(default=False)
    company_id = fields.Many2one(comodel_name='res.company')

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


class SmsSms(models.Model):
    _name = 'sms.sms'
    _description = 'SMS'
    _rec_name = 'mobile'

    message = fields.Text(
        size=256,
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]})
    mobile = fields.Char(
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]})
    gateway_id = fields.Many2one(
        comodel_name='sms.gateway',
        string='SMS Gateway',
        readonly=True,
        states={'draft': [('readonly', False)]})
    state = fields.Selection(selection=[
        ('draft', 'Queued'),
        ('sent', 'Sent'),
        ('cancel', 'Cancel'),
        ('error', 'Error'),
        ], string='Message Status',
        readonly=True,
        default='draft')
    error = fields.Text(
        string='Last Error',
        size=256,
        readonly=True,
        states={'draft': [('readonly', False)]})
    validity = fields.Integer(
        string='Validity',
        readonly=True,
        states={'draft': [('readonly', False)]},
        help='The maximum time -in minute(s)- before the message is dropped.')
    classes = fields.Selection(
        selection=CLASSES_LIST,
        readonly=True,
        states={'draft': [('readonly', False)]},
        help='The sms class: flash(0), phone display(1), SIM(2), toolkit(3)')
    deferred = fields.Integer(
        readonly=True,
        states={'draft': [('readonly', False)]},
        help='The time -in minute(s)- to wait before sending the message.')
    priority = fields.Selection(
        readonly=True,
        states={'draft': [('readonly', False)]},
        selection=PRIORITY_LIST,
        help='The priority of the message ')
    coding = fields.Selection([
        ('1', '7 bit'),
        ('2', 'Unicode')
        ], readonly=True,
        states={'draft': [('readonly', False)]},
        help='The sms coding: 1 for 7 bit or 2 for unicode')
    tag = fields.Char(
        size=256,
        readonly=True,
        states={'draft': [('readonly', False)]},
        help='An optional tag')
    nostop = fields.Boolean(
        string='NoStop',
        readonly=True,
        states={'draft': [('readonly', False)]},
        help='Do not display STOP clause in the message, this requires that'
             'this is not an advertising message.')
    partner_id = fields.Many2one(
        'res.partner',
        readonly=True,
        states={'draft': [('readonly', False)]},
        string='Partner')
    company_id = fields.Many2one(
        comodel_name='res.company',
        readonly=True,
        states={'draft': [('readonly', False)]})

    @api.model
    def _convert_to_e164(self, erp_number):
        to_dial_number = erp_number.replace(u'\xa0', u' ')
        return to_dial_number

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        self.mobile = self.partner_id.mobile

    @api.multi
    def send(self):
        for sms in self:
            if not sms.gateway_id._check_permissions():
                sms.write(
                    {'error': 'no permission on gateway', 'state': 'error'})
                sms._cr.commit()
                return False
            if sms.gateway_id.char_limit and len(sms.message) > 160:
                sms.write({
                    'state': 'error',
                    'error': _('Size of SMS should not be more then 160 char'),
                    })
            if not hasattr(sms, "_send_%s" % sms.gateway_id.method):
                        #may not exist the gateway
                raise UserError(_("No method gateway selected"))
            else:
                try:
                    with sms._cr.savepoint():
                        getattr(sms, "_send_%s" % sms.gateway_id.method)()
                        sms.write({'state': 'sent', 'error': ''})
                except Exception, e:
                    _logger.error('Failed to send sms %s', e)
                    sms.write({'error': e, 'state': 'error'})
                sms._cr.commit()
        return True

    @api.multi
    def cancel(self):
        self.write({'state': 'cancel'})

    @api.multi
    def retry(self):
        self.write({'state': 'draft'})
