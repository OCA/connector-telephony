/*  © 2014-2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
    © 2015-2016 Juris Malinens (port to v9)
    License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).   */

odoo.define('freeswitch_click2dial.click2dial', function (require) {
"use strict";

var UserMenu = require('web.UserMenu');
var WebClient = require('web.WebClient');
var web_client = require('web.web_client');
var Widget = require('web.Widget');
var core = require('web.core');
var _t = core._t;

var click2dial = {};

click2dial.OpenCaller = Widget.extend({
    template: 'freeswitch_click2dial.OpenCaller',

    start: function () {
        this.$('#freeswitch-open-caller').on(
            'click', this.on_open_caller);
        this._super();
    },

    on_open_caller: function (event) {
        event.stopPropagation();
        var self = this;
        self.rpc('/freeswitch_click2dial/get_record_from_my_channel', {}).done(function(r) {
        // console.log('RESULT RPC r='+r);
        // console.log('RESULT RPC type r='+typeof r);
        // console.log('RESULT RPC isNaN r='+isNaN(r));
        if (r === false) {
             self.do_warn(
                _t('Failure'),
                _t('Problem in the connection to FreeSWITCH'),
                false);
        }
        else if (typeof r == 'string' && isNaN(r)) {
             self.do_warn(
                r,
                _t('The calling number is not a phone number!'),
                false);
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
                _t('Moving to %s ID %d', r[0], r[1]),
                false);
            var action = {
                type: 'ir.actions.act_window',
                res_model: r[0],
                res_id: r[1],
                view_mode: 'form,tree',
                views: [[false, 'form']],
                /* If you want to make it work with the 'web' module
                of Odoo Enterprise edition, you have to change the line
                target: 'current',
                  to:
                target: 'new',
                If you want to use target: 'current', with web/enterprise,
                you have to reload the Web page just after */
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
                var freeswitch_button = new click2dial.OpenCaller();
                // attach the phone logo/button to the systray
                freeswitch_button.appendTo($('.oe_systray'));
            });
        },
    });

});
