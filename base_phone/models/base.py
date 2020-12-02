# © 2016 SYLEAM
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models

from .. import common


class Base(models.AbstractModel):
    _inherit = "base"

    def write(self, vals):
        fields_to_convert = common.get_phone_fields(self, vals)
        if fields_to_convert:
            for record in self:
                loc_vals = common.convert_all_phone_fields(
                    record, vals, fields_to_convert
                )
                super(Base, record).write(loc_vals)
            return True
        else:
            return super(Base, self).write(vals)

    @api.model
    def create(self, vals):
        fields_to_convert = common.get_phone_fields(self, vals)
        if fields_to_convert:
            vals = common.convert_all_phone_fields(self, vals, fields_to_convert)
        return super(Base, self).create(vals)
