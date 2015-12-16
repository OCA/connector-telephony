/* Asterisk_click2dial module for Odoo
   Copyright (C) 2014 Alexis de Lattre <alexis@via.ecp.fr>
   The licence is in the file __openerp__.py */

odoo.define('asterisk_click2dial.click2dial', function (require) {

    var UserMenu = require('web.UserMenu');
    var WebClient = require('web.WebClient');
    var web_client = require('web.web_client');
    var Widget = require('web.Widget');
    var core = require('web.core');
    var _t = core._t;

    var click2dial = {};

    click2dial.OpenCaller = Widget.extend({
        template:'asterisk_click2dial.OpenCaller',

        start: function () {
            this.$('#asterisk-open-caller').on(
                'click', this.on_open_caller);
            this._super();
        },

        on_open_caller: function (event) {
            event.stopPropagation();
            var self = this;
            self.rpc('/asterisk_click2dial/get_record_from_my_channel', {}).done(function(r) {
            console.log('RESULT RPC r='+r);
            console.log('RESULT RPC type r='+typeof r);
            if (r === false) {
                 self.do_notify(
                    _t('Failure'),
                    _t('Problem in the connection to Asterisk'));
            }
            else if (typeof r == 'string') {
                 var action = {
                    name: _t('Number Not Found'),
                    type: 'ir.actions.act_window',
                    res_model: 'number.not.found',
                    view_mode: 'form',
                    views: [[false, 'form']],
                    target: 'new',
                    context: {'default_calling_number': r},
                 };
                web_client.action_manager.do_action(action);
 
                }
            else if (typeof r == 'object' && r.length == 3) {
                self.do_notify( // Not working
                    _t('Success'),
                    _t('Moving to %s ID %d', r[0], r[1]));
                var action = {
                    type: 'ir.actions.act_window',
                    res_model: r[0],
                    res_id: r[1],
                    view_mode: 'form,tree',
                    views: [[false, 'form']],
                    target: 'current',
                    context: {},
                };
                web_client.action_manager.do_action(action);
            }
        });
       },
    });

    UserMenu.include({
        do_update: function(){
            this._super.apply(this, arguments);
            this.update_promise.then(function() {
                var asterisk_button = new click2dial.OpenCaller();
                console.log(this);
                asterisk_button.appendTo($('.oe_systray'));
            });
        },
    });

});


