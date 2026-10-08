from odoo import models

from .sms_api import SmsApiGlobalDigital


class ResCompany(models.Model):
    _inherit = "res.company"

    def _get_sms_api_class(self):
        self.ensure_one()
        if self.env["iap.account"].get("sms").provider == "sms_global_digital":
            return SmsApiGlobalDigital
        return super()._get_sms_api_class()
