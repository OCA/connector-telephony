/* Base phone module for Odoo
   Copyright (C) 2013-2018 Akretion France
   @author: Alexis de Lattre <alexis.delattre@akretion.com>
   License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */

odoo.define('base_phone.updatedphone_widget', function (require) {
    "use strict";


    var core = require('web.core');
    var web_client = require('web.web_client');
    var basicFields = require('web.basic_fields');
    var InputField = basicFields.InputField;
    var originalFieldPhone = basicFields.FieldPhone;
    var fieldRegistry = require('web.field_registry');
    var QWeb = core.qweb;
    var _t = core._t;

    var updatedFieldPhone = originalFieldPhone.extend({

/*        init: function () {
            this._super.apply(this, arguments);
            },  */

        _renderReadonly: function() {
            this._super();
            if (this.mode == "readonly") {
                var self = this;
                var phone_num = this.value;
                /* if(phone_num) {
                    phone_num = phone_num.replace(/ /g, '').replace(/-/g, '');
                } */
                /* var click2dial_text = '';
                if (phone_num && !this.options.dial_button_invisible) {
                    click2dial_text = _t('Dial');
                }
                this.$el.filter('#click2dial').off('click');
                this.$el.filter('#click2dial')
                    .text(click2dial_text)
                    .attr('href', '#')
                } */
                this.$el.filter('a[href^="tel:"]').off('click');
                this.$el.filter('a[href^="tel:"]')
                    .on('click', function(ev) {
                        self.do_notify(
                                _t('Click2dial started'),
                                _t('Unhook your ringing phone'),
                                false);
                        var arg = {
                            'phone_number': phone_num,
                            'click2dial_model': self.model,
                            'click2dial_id': self.res_id};
                        self._rpc({
                                route: '/base_phone/click2dial',
                                params: arg,
                                }).done(function(r) {
                            // TODO: check why it never goes in there
                            if (r === false) {
                                self.do_warn("Click2dial failed");
                            } else if (typeof r === 'object') {
                                self.do_notify(
                                        _t('Click2dial successfull'),
                                        _t('Number dialed:') + ' ' + r.dialed_number,
                                        false);
                                if (r.action_model) {
                                    var context = {
                                        'click2dial_model': self.model,
                                        'click2dial_id': self.res_id,
                                        'phone_number': phone_num,
                                    };
                                    var action = {
                                        name: r.action_name,
                                        type: 'ir.actions.act_window',
                                        res_model: r.action_model,
                                        view_mode: 'form',
                                        views: [[false, 'form']],
                                        target: 'new',
                                        context: context,
                                    };
                                    this.do_action(action);
                                }
                            }
                        });
                    });
            }
        }
    });

    // To avoid conflicts, we check that widgets do not exist before using
    /*
    if(!core.form_widget_registry.get('fax')){
        core.form_widget_registry.add('fax', FieldFax);
    }

    if(!core.form_widget_registry.get('phone')){
        core.form_widget_registry.add('phone', FieldPhone);
    }
    */

fieldRegistry.add('phone', updatedFieldPhone);

return updatedFieldPhone;

});
