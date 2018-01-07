/* Base phone module for Odoo
   Copyright (C) 2013-2016 Alexis de Lattre <alexis@via.ecp.fr>
   The licence is in the file __openerp__.py */

odoo.define('base_phone.phone_widget', function (require) {
    "use strict";

    var ajax = require('web.ajax');
    var core = require('web.core');
    var web_client = require('web.web_client');
    var _t = core._t;

    var field_utils = require('web.field_utils');

    // The next line is the super dumb version of the code below:
    field_utils.format.phone = x => x
    field_utils.parse.phone = x => x
    // // The following lines do some UI magic around numbers so people can click things automatically,
    // // I haven't got to understand all around this.
    // // My doubts are mainly around the _format function, since I haven't been able to find
    // // other formatters.
    // var ColumnPhone = Widget.extend({
    //     // ability to add widget="phone" in TREE view
    //     _format: function(row_data, options) {
    //         var phone_num = row_data[this.id].value;
    //         if (phone_num) {
    //             var raw_phone_num = phone_num.replace(/ /g, '');
    //             raw_phone_num = raw_phone_num.replace(/-/g, '');
    //             return _.template("<a href='tel:<%-href%>'><%-text%></a>")({
    //                 href: raw_phone_num,
    //                 text: phone_num
    //             });
    //         }
    //         return this._super(row_data, options);
    //     }
    // });


    // if (!field_registry.get('phone')) {
    //     field_registry.add('field.phone', ColumnPhone);
    // }

    var field_registry = require('web.field_registry');
    var FieldEmail = field_registry.get('email');

    var FieldFax = FieldEmail.extend({
        className: 'o_field_phone',
        prefix: 'fax',
        formatType: 'phone',
        _renderReadonly: function() {
            var phone_num = this.get('value');
            if (phone_num) {
                phone_num = phone_num.replace(/ /g, '').replace(/-/g, '');
                this.$el.attr('href', this.prefix + ':' + phone_num);
            }
            
        },
    });

    var FieldPhone = FieldFax.extend({
        prefix: 'tel',
        isValid: function() {
          var value = this._getValue() || this.value;
          let isValid = (!value || value === 'false') || value.replace && (/^\d{7,}$/).test(value.replace(/[\s()+\-\.]|ext/gi, ''));
          return isValid
        },
        _renderReadonly: function() {
            this._super();
            var self = this
            var phone_num = this.value;
            if (phone_num) {
                phone_num = phone_num.replace(/ /g, '').replace(/-/g, '');
            }
            var click2dial_text = _t('Dial');
            this.$el.text(click2dial_text + ': ' + phone_num);
            this.$el.attr('href', '#');
            this.$el.removeClass('o_text_overflow');
            this.$el.click(function(ev) {
                    ev.preventDefault();
                    self.do_notify(
                            _t('Click2dial started'),
                            _t('Unhook your ringing phone'),
                            false);
                    var specialData = self.record.specialData[this.name];
                    let model = self.model;
                    let id = self.recordData.id;
                    var arg = {
                        'phone_number': phone_num,
                        'click2dial_model': model,
                        'click2dial_id': id};
                    ajax.jsonRpc('/base_phone/click2dial', 'call', arg).then(function(r) {
                        // console.log('Click2dial r=%s', JSON.stringify(r));
                        if (r === false) {
                            self.do_warn("Click2dial failed");
                        } else if (typeof r === 'object') {
                            self.do_notify(
                                    _t('Click2dial successfull'),
                                    _t('Number dialed:') + ' ' + r.dialed_number,
                                    false);
                            if (r.action_model) {
                                var context = {
                                    'click2dial_model': model,
                                    'click2dial_id': id,
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
                                web_client.action_manager.do_action(action);
                            }
                        }
                    });
                });
        }
    });

    field_registry.add('fax', FieldFax);
    field_registry.add('phone', FieldPhone);
});
