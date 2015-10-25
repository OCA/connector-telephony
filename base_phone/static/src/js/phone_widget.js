/* Base phone module for Odoo
   Copyright (C) 2013-2015 Alexis de Lattre <alexis@via.ecp.fr>
   The licence is in the file __openerp__.py */

odoo.define('base_phone.phone_widget', function (require) {
"use strict";

var core = require('web.core');
var formwidgets = require('web.form_widgets');
var _t = core._t;


var FieldPhone = formwidgets.FieldChar.extend({
        template: 'FieldPhone',
        initialize_content: function() {
            this._super();
            var $button = this.$el.find('button');
            $button.click(this.on_button_clicked);
            this.setupFocus($button);
        },
        render_value: function() {
            if (!this.get('effective_readonly')) {
                this._super();
            } else {
                var self = this;
                var phone_num = this.get('value');
                // console.log('BASE_PHONE phone_num = %s', phone_num);
                var href = '#';
                var href_text = '';
                if (phone_num) {
                  href = 'tel:' + phone_num;
                  href_text = formatInternational('', phone_num) || '';
                }
                if (href_text) {
                    this.$el.find('a.oe_form_uri').attr('href', href).text(href_text);
                    this.$el.find('span.oe_form_char_content').text('');
                } else {
                    this.$el.find('a.oe_form_uri').attr('href', '').text('');
                    this.$el.find('span.oe_form_char_content').text(phone_num || '');
                }
                var click2dial_text = '';
                if (href_text && !this.options.dial_button_invisible) {
                  click2dial_text = _t('Dial');
                }
                this.$el.find('#click2dial').off('click');
                this.$el.find('#click2dial')
                    .text(click2dial_text)
                    .on('click', function(ev) {
                        self.do_notify(
                            _t('Click2dial started'),
                            _t('Unhook your ringing phone'));
                        var arg = {
                            'phone_number': phone_num,
                            'click2dial_model': self.view.dataset.model,
                            'click2dial_id': self.view.datarecord.id};
                        self.rpc('/base_phone/click2dial', arg).done(function(r) {
                            // console.log('Click2dial r=%s', JSON.stringify(r));
                            if (r === false) {
                                self.do_warn("Click2dial failed");
                            } else if (typeof r === 'object') {
                                self.do_notify(
                                    _t('Click2dial successfull'),
                                    _t('Number dialed:') + ' ' + r.dialed_number);
                                if (r.action_model) {
                                    var context = {
                                        'click2dial_model': self.view.dataset.model,
                                        'click2dial_id': self.view.datarecord.id,
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
                                    formwidgets.client.action_manager.do_action(action);
                                }
                            }
                        });
                    });
            }
        },
        on_button_clicked: function() {
            location.href = 'tel:' + this.get('value');
        }
    });


var FieldFax = formwidgets.FieldChar.extend({
        template: 'FieldFax',
        initialize_content: function() {
            this._super();
            var $button = this.$el.find('button');
            $button.click(this.on_button_clicked);
            this.setupFocus($button);
        },
        render_value: function() {
            if (!this.get('effective_readonly')) {
                this._super();
            } else {
                var fax_num = this.get('value');
                // console.log('BASE_PHONE fax_num = %s', fax_num);
                var href = '#';
                var href_text = '';
                if (fax_num) {
                    href = 'fax:' + fax_num;
                    href_text = formatInternational('', fax_num) || '';
                }
                if (href_text) {
                    this.$el.find('a.oe_form_uri').attr('href', href).text(href_text);
                    this.$el.find('span.oe_form_char_content').text('');
                } else {
                    this.$el.find('a.oe_form_uri').attr('href', '').text('');
                    this.$el.find('span.oe_form_char_content').text(fax_num || '');
                }
            }
        },
        on_button_clicked: function() {
            location.href = 'fax:' + this.get('value');
        }
    });

core.form_widget_registry
    .add('phone', FieldPhone)
    .add('fax', FieldFax);

/*
var Column = require('web.list_view.js');

var ColumnPhone = Column.extend({
    // ability to add widget="phone" in TREE view
    _format: function(row_data, options) {
        console.log('row_data=' + row_data);
        console.log('options=');
        console.log(options);
        var value = row_data[this.id].value;
        if (value && this.widget === 'phone') {
            return formatInternational('', value);
        }
        console.log('return normal');
        return this._super(row_data, options);
    }
});


core.list_widget_registry.add('field.phone', ColumnPhone);
*/
});
