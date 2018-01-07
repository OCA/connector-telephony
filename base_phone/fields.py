# -*- coding: utf-8 -*-
# © 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields
from operator import attrgetter
import logging
_logger = logging.getLogger(__name__)

try:
    import phonenumbers
except ImportError:
    _logger.debug('Cannot `import phonenumbers`.')


class Fax(fields.Char):
    type = 'fax'

    _slots = {
        'country_field': None,
        'partner_field': None,
    }

    def __init__(
            self, string=fields.Default, country_field=fields.Default,
            partner_field=fields.Default, **kwargs):
        super(Fax, self).__init__(
            string=string, country_field=country_field,
            partner_field=partner_field, **kwargs)

    _related_country_field = property(attrgetter('country_field'))
    _related_partner_field = property(attrgetter('partner_field'))

    def _setup_regular_full(self, model):
        super(Fax, self)._setup_regular_full(model)
        assert self.country_field in model._fields or \
            self.partner_field in model._fields, \
            "field %s with unknown country_field and partner_field" % self

    def convert_to_cache(self, value, record, validate=True):
        res = super(Fax, self).convert_to_cache(
            value, record, validate=validate)
        if res:
            try:
                res_parse = res
                try:
                  res_parse = phonenumbers.parse(res, None)
                except:
                  res_parse = phonenumbers.parse(res, region='US')
                res = phonenumbers.format_number(
                    res_parse, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
                no_break_space = '\u00A0'
                res = res.replace(' ', no_break_space)
            except Exception as e:
                _logger.error('Failed to validate phone number:', e)
        return res


class Phone(Fax):
    type = 'phone'
