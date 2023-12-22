# Copyright 2012-2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models

# phone_validation is not officially in the depends of hr, but we would like
# to have the formatting available in hr, not in event_sms -> do a conditional
# import just to be sure
try:
    from odoo.addons.phone_validation.tools.phone_validation import phone_format
except ImportError:

    def phone_format(
        number,
        country_code,
        country_phone_code,
        force_format="INTERNATIONAL",
        raise_exception=True,
    ):
        return number


class HrEmployeePrivate(models.Model):
    _name = "hr.employee"
    _inherit = ["hr.employee"]
    _phone_name_sequence = 30
    _phone_name_fields = ["mobile_phone"]
    # work_phone is now a computed field that take the value address_id.phone
    # Don't put emergency_phone in _phone_name_fields because it is not a phone
    # number of the employee

    def _phone_format(self, number, country=None):
        """Call phone_validation formatting tool function. Returns original
        number in case formatting cannot be done (no country, wrong info, ...)"""
        if not number or not country:
            return number
        new_number = phone_format(
            number,
            country.code,
            country.phone_code,
            force_format="E164",
            raise_exception=False,
        )
        return new_number if new_number else number

    @api.onchange("mobile_phone")
    def mobile_phone_change(self):
        if self.mobile_phone:
            country = self.env.company.country_id
            self.mobile_phone = self._phone_format(self.mobile_phone, country)

    @api.onchange("emergency_phone")
    def emergency_phone_change(self):
        if self.emergency_phone:
            self.emergency_phone = self._phone_format(self.emergency_phone)
