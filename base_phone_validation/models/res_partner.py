# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C)  cgstudiomap <cgstudiomap@gmail.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import logging
from openerp import models, api
import phonenumbers
from openerp.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _force_validation(self, phonenumber):
        """Force the validation using phonenumbers of a given number

        :param phonenumber: string
        :raise ValidationError: if the given number is not validated.
        """
        number = phonenumbers.parse(phonenumber, self.country_id.code)
        if not phonenumbers.is_valid_number(number):
            error_msg = 'The number "{}" seems not valid for {}.\nPlease double check it.'.format(
                phonenumber, self.country_id.name
            )
            _logger.error(error_msg)
            raise ValidationError(error_msg)

    @api.constrains('phone')
    def _phone_number_validation(self):
        self._force_validation(self.phone)

    @api.constrains('fax')
    def _fax_number_validation(self):
        self._force_validation(self.fax)

    @api.constrains('mobile')
    def _mobile_number_validation(self):
        self._force_validation(self.mobile)
