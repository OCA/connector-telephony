# Copyright 2012-2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class HrApplicant(models.Model):
    _name = "hr.applicant"
    _inherit = ["hr.applicant", "phone.validation.mixin"]
    _phone_name_sequence = 50
    _phone_name_fields = ["partner_phone", "partner_mobile"]

    @api.onchange("partner_phone")
    def partner_phone_change(self):
        if self.partner_phone:
            self.partner_phone = self.phone_format(self.partner_phone)

    @api.onchange("partner_mobile")
    def partner_mobile_change(self):
        if self.partner_mobile:
            self.partner_mobile = self.phone_format(self.partner_mobile)

    def name_get(self):
        if self._context.get("callerid"):
            res = []
            for appl in self:
                if appl.partner_id:
                    name = "%s (%s)" % (appl.partner_id.name, appl.name)
                elif appl.partner_name:
                    name = "%s (%s)" % (appl.partner_name, appl.name)
                else:
                    name = appl.name
                res.append((appl.id, name))
            return res
        else:
            return super().name_get()
