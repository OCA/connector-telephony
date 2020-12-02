# © 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class IrFieldsConverter(models.AbstractModel):
    _inherit = "ir.fields.converter"

    @api.model
    def _str_to_phone(self, model, field, value):
        return super(IrFieldsConverter, self)._str_to_char(model, field, value)

    @api.model
    def _str_to_fax(self, model, field, value):
        return super(IrFieldsConverter, self)._str_to_char(model, field, value)
