# Copyright 2016-2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import models


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
