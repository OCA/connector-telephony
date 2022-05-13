# Copyright 2022 Moka Tourisme (https://www.mokatourisme.fr).
# @author Pierre Verkest <pierreverkest84@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MailNotification(models.Model):
    _inherit = "mail.notification"

    failure_type = fields.Selection(
        selection_add=[
            ("sms_sendinblue_invalid_parameter", "Invalid parameter"),
            ("sms_sendinblue_missing_parameter", "Missing parameter"),
            ("sms_sendinblue_out_of_range", "Out of range"),
            ("sms_sendinblue_campaign_processing", "Campaign processing"),
            ("sms_sendinblue_campaign_sent", "Campaign sent"),
            ("sms_sendinblue_document_not_found", "Document not found"),
            ("sms_sendinblue_reseller_permission_denied", "Reseller permission denied"),
            ("sms_sendinblue_permission_denied", "Permission denied"),
            ("sms_sendinblue_duplicate_parameter", "Duplicate parameter"),
            ("sms_sendinblue_duplicate_request", "Duplacate request"),
            ("sms_sendinblue_method_not_allowed", "Method not allowed"),
            ("sms_sendinblue_account_under_validation", "Account under validation"),
            ("sms_sendinblue_not_acceptable", "Not acceptable"),
        ]
    )
