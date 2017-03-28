# coding: utf-8
# Copyright (C) 2015 Sébastien BEAU <sebastien.beau@akretion.com>
# Valentin CHEMIERE <valentin.chemiere@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields
from functools import wraps


def implemented_by_provider(func):
    """Decorator: call _provider_prefixed method instead.
    Usage:
        @implemented_by_provider
        def _do_something()
        def _laposte_do_something()
        def _gls_do_something()
    At runtime, sms-client._do_something() will try to call
    the provider spectific method or fallback to generic _do_something
    """
    @wraps(func)
    def wrapper(cls, *args, **kwargs):
        fun_name = func.__name__
        fun = '_%s%s' % (cls.provider_type, fun_name)
        if not hasattr(cls, fun):
            fun = '_provider%s' % (fun_name)
            # return func(cls, *args, **kwargs)
        return getattr(cls, fun)(*args, **kwargs)
    return wrapper


OVH_KEYCHAIN_NAMESPACE = 'ovh_provider'


class AccountProduct(models.Model):
    _inherit = 'keychain.account'

    namespace = fields.Selection(
        selection_add=[(OVH_KEYCHAIN_NAMESPACE, 'Ovh_sms')])

    def _ovh_provider_init_data(self):
        return {'sms_account': ""}

    def _ovh_provider_validate_data(self, data):

        return True
