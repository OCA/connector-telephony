# Copyright 2023 ForgeFlow S.L. (https://www.forgeflow.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields, models


class TwilioPhoneNumber(models.Model):
    _name = "twilio.phone.number"
    _description = "Twilio Phone Number"

    name = fields.Char(string="Friendly Name")
    phone_number = fields.Char()
    has_sms_enabled = fields.Boolean(string="SMS Enabled")
    sid = fields.Char(string="SID")

    _sql_constraints = [
        (
            "uniq_phone_sid",
            "unique(sid)",
            "You already have this sid used in other record",
        ),
        (
            "uniq_phone_number",
            "unique(phone_number)",
            "You already have this phone number used in other record",
        ),
    ]
