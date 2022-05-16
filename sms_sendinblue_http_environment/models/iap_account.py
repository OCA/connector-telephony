# Copyright 2022 Moka Tourisme (https://www.mokatourisme.fr).
# @author Pierre Verkest <pierreverkest84@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class IapAccount(models.Model):
    _inherit = "iap.account"

    @property
    def _server_env_fields(self):
        res = super()._server_env_fields
        res.update(
            {
                "sms_sendinblue_http_api_key": {},
                "sms_sendinblue_http_from": {},
            }
        )
        return res
