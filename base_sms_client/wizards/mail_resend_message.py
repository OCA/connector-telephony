# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class MailResendMessage(models.TransientModel):

    _inherit = 'mail.resend.message'

    @api.multi
    def resend_mail_action(self):
        wizards = self.filtered(
            lambda w: w.mail_message_id.message_type == "sms"
        )
        if wizards:
            sms_to_re_send = self.env['sms.sms'].search(
                [
                    (
                        'mail_message_id',
                        'in',
                        wizards.mapped('mail_message_id.id'),
                    )
                ]
            )
            sms_to_re_send.retry()
            message_ids = sms_to_re_send.mapped('mail_message_id')
            notification_ids = sms_to_re_send.mapped(
                'mail_message_id.notification_ids'
            ).sudo()
            notification_ids.write({'email_status': 'ready'})
            message_ids._notify_failure_update()
        return super(
            MailResendMessage,
            self.filtered(lambda w: w.mail_message_id.message_type != "sms"),
        ).resend_mail_action()
