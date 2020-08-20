# Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
# Copyright (C) 2011 SYLEAM (<http://syleam.fr/>)
# Copyright (C) 2013 Julius Network Solutions SARL <contact@julius.fr>
# Copyright (C) 2015 Valentin Chemiere <valentin.chemiere@akretion.com>
# Copyright (C) 2015 Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)


class SmsSms(models.Model):
    _name = 'sms.sms'
    _description = 'SMS'
    _rec_name = 'mobile'
    _inherits = {'mail.message': 'mail_message_id'}
    _inherit = ['sms.abstract']

    message = fields.Text(
        size=256,
        required=True,
        readonly=True,
        translate=False,
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
    partner_id = fields.Many2one(
        'res.partner',
        readonly=True,
        states={'draft': [('readonly', False)]},
        string='Partner')
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

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        self.mobile = self.partner_id.mobile

    # commit is use to not loose each sms state with orm rollback
    @api.multi
    def _check_gateway_method(self):
        self.ensure_one()
        if self.gateway_id.method:
            return True
        else:
            self.write({
                'state': 'error',
                'error': _("No method gateway selected ")})
            return False

    @api.multi
    def _check_gateway_permission(self):
        self.ensure_one()
        if self.sudo(self.create_uid.id).gateway_id._check_permissions():
            return True
        else:
            self.write(
                {'error': 'no permission on gateway', 'state': 'error'})
            return False

    @api.multi
    def _check_sms_length(self):
        self.ensure_one()
        if len(self.message) <= self.gateway_id.char_limit:
            return True
        else:
            self.write({
                'state': 'error',
                'error': _("Size of SMS should not be more than %s "
                           "characters ") % self.sms.gateway_id.char_limit
            })
            return False

    @api.multi
    def send(self):
        allsend_ok = True
        for sms in self:
            sms_check = True
            if not sms._check_gateway_method():
                allsend_ok = False
                sms_check = False
                continue
            if not sms._check_gateway_permission():
                allsend_ok = False
                sms_check = False
                continue
            if not sms._check_sms_length():
                allsend_ok = False
                sms_check = False
                continue
            if sms_check:
                try:
                    with sms._cr.savepoint():
                        getattr(sms, "_send_%s" % sms.gateway_id.method)()
                        sms.write({'state': 'sent', 'error': ''})
                        if (
                            sms.mail_message_id
                            and sms.mail_message_id.notification_ids
                        ):
                            sms.mail_message_id.notification_ids.sudo().write(
                                {'email_status': 'sent'}
                            )
                except Exception as e:
                    _logger.error('Failed to send sms %s', e)
                    sms.write({'error': e, 'state': 'error'})
                    if (
                        sms.mail_message_id
                        and sms.mail_message_id.notification_ids
                    ):
                        sms.mail_message_id.notification_ids.sudo().write(
                            {'email_status': 'exception', 'failure_reason': e}
                        )
        return allsend_ok

    @api.multi
    def cancel(self):
        self.write({'state': 'cancel'})
        for rec in self:
            if rec.mail_message_id and rec.mail_message_id.notification_ids:
                rec.mail_message_id.notification_ids.sudo().write(
                    {'email_status': 'canceled'}
                )

    @api.multi
    def retry(self):
        self.write({'state': 'draft'})
