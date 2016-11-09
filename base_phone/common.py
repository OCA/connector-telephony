# -*- coding: utf-8 -*-
# © 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from . import fields as phone_fields
import logging
_logger = logging.getLogger(__name__)

try:
    import phonenumbers
except ImportError:
    _logger.debug('Cannot `import phonenumbers`.')


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
                # Warning: when we edit or create a partner from the
                # POS frontend vals[country_key] is a string !
                country = self.env['res.country'].browse(
                    int(vals[country_key]))
            else:
                country = self[country_key]
        if partner_key and not country:
            if partner_key in loc_vals:
                partner = self.env['res.partner'].browse(
                    int(vals[partner_key]))
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
        if isinstance(self._fields.get(key), phone_fields.Fax):
            fields_to_convert.append(key)
    return fields_to_convert
