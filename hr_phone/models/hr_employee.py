# Copyright 2012-2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models

from odoo.addons.phone_validation.tools import phone_validation


class HrEmployeePrivate(models.Model):
    _inherit = "hr.employee"
    _phone_name_sequence = 30

    def _phone_get_number_fields(self):
        # work_phone is now a computed field that take the value address_id.phone
        # Don't put emergency_phone in _phone_name_fields because it is not a phone
        # number of the employee
        return ["mobile_phone"]

    @api.onchange("mobile_phone")
    def mobile_phone_change(self):
        if self.mobile_phone:
            self.mobile_phone = self._phone_format(self.mobile_phone)

    @api.onchange("emergency_phone")
    def emergency_phone_change(self):
        if self.emergency_phone:
            self.emergency_phone = self._phone_format(self.emergency_phone)

    def _phone_format(self, number, country=None):
        country = country or self.country_id or self.env.company.country_id
        if not country:
            return number
        return phone_validation.phone_format(
            number,
            country.code if country else None,
            country.phone_code if country else None,
            force_format="INTERNATIONAL",
            raise_exception=False,
        )
