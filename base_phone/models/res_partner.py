# Copyright 2016-2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import models


class ResPartner(models.Model):
    _inherit = "res.partner"
    _phone_name_sequence = 10
    _phone_name_fields = ["phone", "mobile"]

    def _compute_display_name(self):
        res = super()._compute_display_name()
        if self._context.get("callerid"):
            for partner in self:
                if partner.parent_id and partner.parent_id.is_company:
                    name = f"{partner.parent_id.name}, {partner.name}"
                else:
                    name = partner.name
                partner.display_name = name.strip()
        return res
