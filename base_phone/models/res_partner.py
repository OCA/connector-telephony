# Copyright 2016-2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, models

from odoo.addons.phone_validation.tools import phone_validation


class ResPartner(models.Model):
    _inherit = "res.partner"

    _phone_name_sequence = 10

    def name_get(self):
        if self._context.get("callerid"):
            res = []
            for partner in self:
                if partner.parent_id and partner.parent_id.is_company:
                    name = "{}, {}".format(partner.parent_id.name, partner.name)
                else:
                    name = partner.name
                res.append((partner.id, name))
            return res
        else:
            return super().name_get()

    @api.onchange("phone", "mobile", "country_id", "parent_id")
    def _onchange_phone_validation(self):
        origin = self.browse(self.id.origin)
        origin_country = origin.country_id
        if origin_country and (origin_country != self.country_id):
            # Go back to national format before changing country
            if self.phone:
                self.phone = self._phone_format(
                    self.phone,
                    country=origin_country,
                    force_format="NATIONAL",
                )
            if self.mobile:
                self.mobile = self._phone_format(
                    self.mobile,
                    country=origin_country,
                    force_format="NATIONAL",
                )
                super()._onchange_mobile_validation()
        super()._onchange_phone_validation()
        return

    def _phone_format(
        self,
        number,
        country=None,
        company=None,
        force_format="INTERNATIONAL",
    ):
        # Copied from Odoo source addons/phone_validation/models/res_partner.py
        country = (
            country
            or self.country_id
            # First change, to utilize company variable
            or (company and company.country_id)
            or self.env.company.country_id
        )
        if not country:
            return number
        res = phone_validation.phone_format(
            number,
            country.code if country else None,
            country.phone_code if country else None,
            # Second change, to have flexibility in number format
            force_format=force_format,
            raise_exception=False,
        )
        return res
