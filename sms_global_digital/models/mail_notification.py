from odoo import fields, models


class MailNotification(models.Model):
    _inherit = "mail.notification"

    failure_type = fields.Selection(
        selection_add=[("sms_test", "Test Mode: SMS not sent")]
    )
