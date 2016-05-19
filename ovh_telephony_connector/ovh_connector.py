# -*- coding: utf-8 -*-
##############################################################################
#
#    OVH connector module for Odoo
#    Copyright (C) 2015 Alexis de Lattre <alexis@via.ecp.fr>
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

from openerp import models, fields, api, _
from openerp.exceptions import UserError
import logging

try:
    # -> pip install SOAPpy
    from SOAPpy import WSDL
except ImportError:
    WSDL = None

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = "res.users"

    ovh_billing_number = fields.Char(string='OVH Billing Number')
    ovh_calling_number = fields.Char(
        string="OVH Calling Number", help="The phone number that will "
        "be presented during a click2dial")
    ovh_click2call_login = fields.Char(string='OVH Click2call Login')
    ovh_click2call_password = fields.Char(
        string="OVH Click2call Password")


class PhoneCommon(models.AbstractModel):
    _inherit = 'phone.common'

    @api.model
    def click2dial(self, erp_number):
        res = super(PhoneCommon, self).click2dial(erp_number)
        if not erp_number:
            raise UserError(
                _('Missing phone number'))

        user = self.env.user
        if not user.ovh_billing_number:
            raise UserError(
                _('Missing OVH Billing Number on user %s') % user.name)

        if not user.ovh_calling_number:
            raise UserError(
                _('Missing OVH Calling Number on user %s') % user.name)

        if not user.ovh_click2call_login:
            raise UserError(
                _('Missing OVH Click2call Login on user %s') % user.name)

        if not user.ovh_click2call_password:
            raise UserError(
                _('Missing OVH Click2dial Password on user %s') % user.name)

        soap = WSDL.Proxy('https://www.ovh.com/soapi/soapi-re-1.63.wsdl')

        called_number = self.convert_to_dial_number(erp_number)
        _logger.debug(
            'Starting OVH telephonyClick2CallDo request with '
            'login = %s billing number = %s calling number = %s '
            'and called_number = %s',
            user.ovh_click2call_login, user.ovh_billing_number,
            user.ovh_calling_number, called_number)

        try:
            soap.telephonyClick2CallDo(
                user.ovh_click2call_login,
                user.ovh_click2call_password,
                user.ovh_calling_number,
                called_number,
                user.ovh_billing_number)
            _logger.info("OVH telephonyClick2CallDo successfull")

        except Exception, e:
            _logger.error(
                "Error in the OVH telephonyClick2CallDo request")
            _logger.error(
                "Here are the details of the error: '%s'", unicode(e))
            raise UserError(
                _("Click to call to OVH failed.\nHere is the error: "
                    "'%s'")
                % unicode(e))

        res['dialed_number'] = called_number
        return res
