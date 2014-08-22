/* Asterisk_click2dial module for OpenERP
   Copyright (C) 2014 Alexis de Lattre <alexis@via.ecp.fr>
   The licence is in the file __openerp__.py */

openerp.asterisk_click2dial = function (instance) {

    var _t = instance.web._t;

    instance.web.OpenCallingPartner = instance.web.Widget.extend({
        template:'asterisk_click2dial.OpenCallingPartner',

        start: function () {
            this.$('#asterisk-open-calling-partner').on(
                'click', this.on_open_calling_partner);
            this._super();
        },

        on_open_calling_partner: function (event) {
            event.stopPropagation();
            var action = {
                name: _t('Open Calling Partner'),
                type: 'ir.actions.act_window',
                res_model: 'wizard.open.calling.partner',
                view_mode: 'form',
                views: [[false, 'form']],
                target: 'new',
                context: {},
            };
            instance.client.action_manager.do_action(action);
       },
    });

    instance.web.UserMenu.include({
        do_update: function(){
            this._super.apply(this, arguments);
            this.update_promise.then(function() {
                var asterisk_button = new instance.web.OpenCallingPartner();
                asterisk_button.appendTo(instance.webclient.$el.find('.oe_systray'));
            });
        },
    });

};


