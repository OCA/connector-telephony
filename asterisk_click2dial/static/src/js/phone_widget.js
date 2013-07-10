// Base phone module for OpenERP
// Copyright (C) 2013 Alexis de Lattre <alexis@via.ecp.fr>
// The licence is in the file __openerp__.py

openerp.asterisk_click2dial = function (instance) {


    instance.asterisk_click2dial.FieldPhone = instance.web.form.FieldChar.extend({
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
                    .attr('href', 'callto:' + this.get('value'))
                    .text(formatted_number || '');
            }
        },
        on_button_clicked: function() {
            location.href = 'callto:' + this.get('value');
        }
    });

    instance.web.form.widgets.add('phone', 'instance.asterisk_click2dial.FieldPhone');

        }
