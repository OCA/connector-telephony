# Copyright 2018-2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import models


class BaseModel(models.AbstractModel):
    _inherit = "base"

    def _phone_format_number(
        self, number, country, force_format="E164", raise_exception=False
    ):
        if "country_id" in self and self.country_id:
            country = self.country_id
        if "partner_id" in self and self.partner_id and self.partner_id.country_id:
            country = self.partner_id.country_id
        return super()._phone_format_number(
            number, country, force_format, raise_exception
        )
