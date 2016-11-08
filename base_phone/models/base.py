# -*- coding: utf-8 -*-
# © 2016 SYLEAM
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .. import common
from odoo import models, api


class Base(models.AbstractModel):
    _inherit = 'base'

    @api.multi
    def write(self, vals):
        fields_to_convert = common.get_phone_fields(self, vals)
        if fields_to_convert:
            for record in self:
                loc_vals = common.convert_all_phone_fields(
                    record, vals, fields_to_convert)
                super(Base, record).write(loc_vals)
            return True
        else:
            return super(Base, self).write(vals)

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        fields_to_convert = common.get_phone_fields(self, vals)
        if fields_to_convert:
            vals = common.convert_all_phone_fields(
                self, vals, fields_to_convert)
        return super(Base, self).create(vals)
