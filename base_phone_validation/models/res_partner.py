# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux , Jordi Riera <kender.jr@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging
from odoo import models, api, _
from odoo.exceptions import ValidationError

try:
    import phonenumbers
except ImportError:
        raise ImportError()

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _force_validation(self, phonenumber, fieldname):
        """Force the validation using phonenumbers of a given number

        :param phonenumber: string
        :param str fieldname: name of the field the number is related to.
        :raise ValidationError: if the given number is not validated.
        """
        number = phonenumbers.parse(phonenumber, self.country_id.code or None)
        if not phonenumbers.is_valid_number_for_region(
                number, self.country_id.code):
            error_msg = u'\n'.join([
                _(u'The number ({}) "{}" seems not valid for {}.').format(
                    fieldname, phonenumber, self.country_id.name
                ),
                _(u'Please double check it.')
            ])
            raise ValidationError(error_msg)

    @api.constrains('phone')
    def _phone_number_validation(self):
        if self.phone:
            self._force_validation(self.phone, 'phone')

    @api.constrains('fax')
    def _fax_number_validation(self):
        if self.fax:
            self._force_validation(self.fax, 'fax')

    @api.constrains('mobile')
    def _mobile_number_validation(self):
        if self.mobile:
            self._force_validation(self.mobile, 'mobile')
