/* Base phone module for OpenERP
   Copyright (C) 2013-2014 Alexis de Lattre <alexis@via.ecp.fr>
   The licence is in the file __openerp__.py */

openerp.base_phone = function (instance) {

    var _t = instance.web._t;

    instance.base_phone.FieldPhone = instance.web.form.FieldChar.extend({
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
                this.$el.find('a.oe_form_uri')
                    .attr('href', 'tel:' + phone_num)
                    .text(phone_num && formatInternational('', phone_num) || '');
                this.$el.find('#click2dial')
                    .text(phone_num && 'Dial' || '')
                    .on('click', function(ev) {
                        self.do_notify(
                            _t('Click2dial started'),
                            _t('Unhook your ringing phone'));
                        var arg = {
                            'phone_number': phone_num,
                            'click2dial_model': self.view.dataset.model,
                            'click2dial_id': self.view.datarecord.id};
                        self.rpc('/base_phone/click2dial', arg).done(function(r) {
                            if (r === false) {
                                self.do_warn("Click2dial failed");
                            } else {
                                self.do_notify(_t('Click2dial successfull'), '');
                                if (typeof r === 'object') {
                                    var context = {};
                                    if (self.view.dataset.model == 'res.partner') {
                                        context = {
                                            'partner_id': self.view.datarecord.id};
                                        }
                                    var action = {
                                        name: r.name,
                                        type: 'ir.actions.act_window',
                                        res_model: r.res_model,
                                        view_mode: 'form',
                                        views: [[false, 'form']],
                                        target: 'new',
                                        context: context,
                                        };
                                    instance.client.action_manager.do_action(action);
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

    instance.web.form.widgets.add('phone', 'instance.base_phone.FieldPhone');

    instance.base_phone.FieldFax = instance.web.form.FieldChar.extend({
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
                this.$el.find('a.oe_form_uri')
                    .attr('href', 'fax:' + fax_num)
                    .text(fax_num && formatInternational('', fax_num) || '');
            }
        },
        on_button_clicked: function() {
            location.href = 'fax:' + this.get('value');
        }
    });

    instance.web.form.widgets.add('fax', 'instance.base_phone.FieldFax');

}
