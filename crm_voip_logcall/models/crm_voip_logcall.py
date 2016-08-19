# -*- coding: utf-8 -*-
##############################################################################
#
#    Phone Log-call module for Odoo/OpenERP
#    Copyright (C) 2016 credativ Ltd (<http://credativ.co.uk>).
#    Copyright (C) 2016 Trever L. Adams
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

from openerp import models, api
import logging


logger = logging.getLogger(__name__)


class PhoneCommon(models.AbstractModel):
    _inherit = 'phone.common'

    @api.model
    def _get_ucp_url(self, users):
        base_url = params.get_param('crm.voip.ucp_url', default='http://localhost/ucp?quietmode=1&module=cdr&command=download&msgid={odoo_uniqueid}&type=download&format=wav&ext={caller_user}')
        return base_url
