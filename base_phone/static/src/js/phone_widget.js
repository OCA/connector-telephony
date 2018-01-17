/* Base phone module for Odoo
   Copyright (C) 2013-2016 Alexis de Lattre <alexis@via.ecp.fr>
   The licence is in the file __openerp__.py */

odoo.define('base_phone.phone_widget', function (require) {
    "use strict";

    var core = require('web.core');
    var formwidgets = require('web.form_widgets');
    var web_client = require('web.web_client');
    var _t = core._t;

    var FieldFax = formwidgets.FieldEmail.extend({
        template: 'FieldFax',
        prefix: 'fax',
        initialize_content: function() {
            this._super();
            var $button = this.$el.find('button');
            $button.click(this.on_button_clicked);
            this.setupFocus($button);
        },
        render_value: function() {
            this._super();
            if (this.get("effective_readonly") && this.clickable) {
                var phone_num = this.get('value');
                if(phone_num) {
                    phone_num = phone_num.replace(/ /g, '').replace(/-/g, '');
                    this.$el.attr('href', this.prefix + ':' + phone_num);
                }
            }
        },
        on_button_clicked: function() {
            location.href = this.prefix + ':' + this.get('value');
        }
    });

    var FieldPhone = FieldFax.extend({
        template: 'FieldPhone',
        prefix: 'tel',
        render_value: function() {
            this._super();
            if (this.get("effective_readonly") && this.clickable) {
                var self = this;
                var phone_num = this.get('value');
                if(phone_num) {
                    phone_num = phone_num.replace(/ /g, '').replace(/-/g, '');
                }
                var click2dial_text = '';
                if (phone_num && !this.options.dial_button_invisible) {
                    click2dial_text = _t('Dial');
                }
                this.$el.filter('#click2dial').off('click');
                this.$el.filter('#click2dial')
                    .text(click2dial_text)
                    .attr('href', '#')
                    .on('click', function(ev) {
                        self.do_notify(
                                _t('Click2dial started'),
                                _t('Unhook your ringing phone'),
                                false);
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
                                        _t('Number dialed:') + ' ' + r.dialed_number,
                                        false);
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
                                    web_client.action_manager.do_action(action);
                                }
                            }
                        });
                    });
            }
        }
    });

    // To avoid conflicts, we check that widgets do not exist before using
    if(!core.form_widget_registry.get('fax')){
        core.form_widget_registry.add('fax', FieldFax);
    }

    if(!core.form_widget_registry.get('phone')){
        core.form_widget_registry.add('phone', FieldPhone);
    }


    var treewidgets = require('web.ListView');

    var ColumnPhone = treewidgets.Column.extend({
        // ability to add widget="phone" in TREE view
        _format: function(row_data, options) {
            var phone_num = row_data[this.id].value;
            if (phone_num) {
                var raw_phone_num = phone_num.replace(/ /g, '');
                raw_phone_num = raw_phone_num.replace(/-/g, '');
                return _.template("<a href='tel:<%-href%>'><%-text%></a>")({
                    href: raw_phone_num,
                    text: phone_num
                });
            }
            return this._super(row_data, options);
        }
    });


    if (!core.list_widget_registry.get('phone')) {
        core.list_widget_registry.add('field.phone', ColumnPhone);
    }

});
