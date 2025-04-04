# Copyright 2016-2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, models


class ResPartner(models.Model):
    _name = "res.partner"
    # inherit on phone.validation.mixin (same as in crm_phone_validation,
    # but base_phone only depends on phone_validation,
    # not on crm_phone_validation)
    _inherit = ["res.partner", "phone.validation.mixin"]
    _phone_name_sequence = 10
    _phone_name_fields = ["phone", "mobile"]

    @api.depends("name")
    @api.depends_context("callerid")
    def _compute_display_name(self):
        if self._context.get("callerid"):
            for partner in self:
                if partner.parent_id and partner.parent_id.is_company:
                    name = f"{partner.parent_id.name}, {partner.name}"
                else:
                    name = partner.name or ""
                partner.display_name = name

        return super()._compute_display_name()
