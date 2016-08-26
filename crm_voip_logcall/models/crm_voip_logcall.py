# -*- coding: utf-8 -*-
# (c) 2016 credativ Ltd (<http://credativ.co.uk>).
# (c) 2016 Trever L. Adams
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, api
import logging


logger = logging.getLogger(__name__)


class PhoneCommon(models.AbstractModel):
    _inherit = 'phone.common'

    @api.model
    def _get_ucp_url(self, users):
        base_url = params.get_param('crm.voip.ucp_url', default='http://localhost/ucp?quietmode=1&module=cdr&command=download&msgid={odoo_uniqueid}&type=download&format=wav&ext={caller_user}')
        return base_url
