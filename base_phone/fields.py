# -*- coding: utf-8 -*-
# © 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import api, fields, models
from operator import attrgetter
import logging

_logger = logging.getLogger(__name__)

try:
    import phonenumbers
except ImportError:
    _logger.debug('Cannot `import phonenumbers`.')


class Phone(fields.Char):

    _slots = {
        'country_field': None,
        'partner_field': None,
    }

    def __init__(
            self, string=None, country_field=None, partner_field=None,
            **kwargs):
        super(Phone, self).__init__(
            string=string, country_field=country_field,
            partner_field=partner_field, **kwargs)

    _related_country_field = property(attrgetter('country_field'))
    _related_partner_field = property(attrgetter('partner_field'))

    def _setup_regular_full(self, model):
        super(Phone, self)._setup_regular_full(model)
        assert self.country_field in model._fields or \
            self.partner_field in model._fields, \
            "field %s with unknown country_field and partner_field" % self

    def convert_to_cache(self, value, record, validate=True):
        res = super(Phone, self).convert_to_cache(
            value, record, validate=validate)
        # print 'db value', res
        if res:
            try:
                res_parse = phonenumbers.parse(res)
                res = phonenumbers.format_number(
                    res_parse, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
                no_break_space = u'\u00A0'
                res = res.replace(' ', no_break_space)
            except:
                pass
        # print 'cache value', res
        return res


def convert_phone_field(value, country_code):
    _logger.debug(
        'convert_phone_field value=%s country=%s', value, country_code)
    try:
        res_parse = phonenumbers.parse(
            value, country_code)
        _logger.debug('res_parse=%s', res_parse)
        new_value = phonenumbers.format_number(
            res_parse, phonenumbers.PhoneNumberFormat.E164)
        _logger.debug('new_value=%s', new_value)
    except:
        _logger.error(
            "Cannot reformat the phone number '%s' to "
            "international format with region=%s",
            value, country_code)
        new_value = value
    return new_value


def convert_all_phone_fields(self, vals, fields_to_convert):
    loc_vals = vals.copy()
    for field in fields_to_convert:
        country_key = self._fields[field].country_field
        partner_key = self._fields[field].partner_field
        country = False
        if country_key:
            if country_key in loc_vals:
                country = self.env['res.country'].browse(vals[country_key])
            else:
                country = self[country_key]
        if partner_key and not country:
            if partner_key in loc_vals:
                partner = self.env['res.partner'].browse(vals[partner_key])
            else:
                partner = self[partner_key]
            if partner:
                country = partner.country_id
        if not country:
            country = self.env.user.company_id.country_id
        country_code = False
        if country:
            country_code = country.code.upper()
        if loc_vals[field]:
            loc_vals[field] = convert_phone_field(
                loc_vals[field], country_code)
    return loc_vals


def get_phone_fields(self, vals):
    fields_to_convert = []
    for key in vals:
        if isinstance(self._fields.get(key), Phone):
            fields_to_convert.append(key)
    return fields_to_convert

original_write = models.Model.write
original_create = models.Model.create


@api.multi
def write(self, vals):
    fields_to_convert = get_phone_fields(self, vals)
    if fields_to_convert:
        for record in self:
            loc_vals = convert_all_phone_fields(
                record, vals, fields_to_convert)
            original_write(record, loc_vals)
        return True
    else:
        return original_write(self, vals)


@api.model
@api.returns('self', lambda value: value.id)
def create(self, vals):
    fields_to_convert = get_phone_fields(self, vals)
    if fields_to_convert:
        vals = convert_all_phone_fields(self, vals, fields_to_convert)
    return original_create(self, vals)

models.Model.write = write
models.Model.create = create
