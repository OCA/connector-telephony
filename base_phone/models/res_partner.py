# -*- coding: utf-8 -*-
# © 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from openerp import models, api
from openerp.addons.base_phone import fields


class ResPartner(models.Model):
    _inherit = 'res.partner'
    _phone_name_sequence = 10

    phone = fields.Phone(country_field='country_id', partner_field='parent_id')
    mobile = fields.Phone(
        country_field='country_id', partner_field='parent_id')
    fax = fields.Phone(country_field='country_id', partner_field='parent_id')

    @api.multi
    def name_get(self):
        if self._context.get('callerid'):
            res = []
            for partner in self:
                if partner.parent_id and partner.parent_id.is_company:
                    name = u'%s (%s)' % (partner.name, partner.parent_id.name)
                else:
                    name = partner.name
                res.append((partner.id, name))
            return res
        else:
            return super(ResPartner, self).name_get()
