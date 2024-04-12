# Copyright 2018-2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import models

from odoo.addons.phone_validation.tools import phone_validation


class PhoneValidationMixin(models.AbstractModel):
    _name = "phone.validation.mixin"
    _description = "Phone Validation Mixin"

    def _phone_get_country(self):
        if "country_id" in self and self.country_id:
            return self.country_id
        if "partner_id" in self and self.partner_id and self.partner_id.country_id:
            return self.partner_id.country_id
        return self.env.company.country_id

    def phone_format(self, number, country=None, company=None):
        country = country or self._phone_get_country()
        if not country:
            return number
        return phone_validation.phone_format(
            number,
            country.code if country else None,
            country.phone_code if country else None,
            force_format="INTERNATIONAL",
            raise_exception=False,
        )
