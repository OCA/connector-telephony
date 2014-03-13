// Base phone module for OpenERP
// Copyright (C) 2013-2014 Alexis de Lattre <alexis@via.ecp.fr>
// The licence is in the file __openerp__.py

openerp.base_phone = function (instance) {


    instance.base_phone.FieldPhone = instance.web.form.FieldChar.extend({
        template: 'FieldPhone',
        initialize_content: function() {
            this._super();
            var $button = this.$el.find('button');
            $button.click(this.on_button_clicked);
            this.setupFocus($button);
        },
        render_value: function() {
            if (!this.get("effective_readonly")) {
                this._super();
            } else {
                var formatted_number = formatInternational('', this.get('value'))
                this.$el.find('a')
                    .attr('href', 'tel:' + this.get('value'))
                    .text(formatted_number || '');
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
            if (!this.get("effective_readonly")) {
                this._super();
            } else {
                var formatted_number = formatInternational('', this.get('value'))
                this.$el.find('a')
                    .attr('href', 'fax:' + this.get('value'))
                    .text(formatted_number || '');
            }
        },
        on_button_clicked: function() {
            location.href = 'fax:' + this.get('value');
        }
    });

    instance.web.form.widgets.add('fax', 'instance.base_phone.FieldFax');

}
