from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    cloudcti_base_url = fields.Char(
        "CloudCTI Base URL",
        default="https://api.cloudcti.nl/api/v2"
    )
    cloudcti_out_url = fields.Char(
        "CloudCTI Signin URL",
        default="https://useraccount.cloudcti.nl/phone/api/callcontrol"
    )
    cloudcti_signin_url = fields.Char(
        "CloudCTI Signin URL",
        default="https://signin-va.cloudcti.nl/signin/api/token"
    )
    cloudcti_subscription_url = fields.Char(
        "CloudCTI Subscription URL",
        default="https://useraccount.cloudcti.nl/phone/api/Subscription"
    )
    cloudcti_popup_time = fields.Integer(
        string="Popup Time (Sec)",
        default=5
    )

    def get_popup_time(self):
        return self.sudo().cloudcti_popup_time


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    popup_time = fields.Integer(
        related='company_id.cloudcti_popup_time',
        readonly=False)
