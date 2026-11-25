# Copyright (C) 2021 Akretion (<http://www.akretion.com>).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class SmsSms(models.Model):
    _inherit = "sms.sms"

    @api.model_create_multi
    def create(self, vals_list):
        if self._context.get("force_sms_body"):
            for vals in vals_list:
                vals["body"] = self._context["force_sms_body"]
        return super().create(vals_list)
