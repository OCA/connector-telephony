# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.sms.tools.sms_api import (
    SmsApi as OdooSmsApi,
)
from odoo.addons.sms.tools.sms_api import (
    SmsApiBase as OdooSmsApiBase,
)


class SmsApiBase(OdooSmsApiBase):
    KEY = ""
    NAME = ""
    DESCRIPTION = "Please enter a Gateway Type."

    def __init__(self, env, account=None):
        super().__init__(env, account)
        if not self.KEY:
            raise NotImplementedError("Subclasses must define KEY")
        if not self.NAME:
            raise NotImplementedError("Subclasses must define NAME")


class SmsApi(SmsApiBase, OdooSmsApi):
    KEY = "iap"
    NAME = "Odoo IAP"
    DESCRIPTION = "This is the Default Odoo IAP sms sending gateway."
