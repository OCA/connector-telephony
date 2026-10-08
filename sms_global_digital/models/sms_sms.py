from odoo import models

from .sms_api import SmsApiGlobalDigital


class SmsSms(models.Model):
    _inherit = "sms.sms"

    def _split_by_api(self):
        account = self.env["iap.account"].get("sms")
        if account.provider == "sms_global_digital":
            yield SmsApiGlobalDigital(self.env, account=account), self
        else:
            yield from super()._split_by_api()
