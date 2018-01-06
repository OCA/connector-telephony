/*  © 2014-2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
    © 2015-2016 Juris Malinens (port to v9)
    License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).   */

odoo.define('asterisk_click2dial.click2dial', function (require) {
"use strict";

var SystrayMenu = require('web.SystrayMenu');
var web_client = require('web.web_client');
var Widget = require('web.Widget');
var core = require('web.core');
var _t = core._t;

var click2dial = {};

var click2dialOpenCaller = Widget.extend({
    template: 'asterisk_click2dial.OpenCaller',
    events: {
        'click': 'on_open_caller',
    },

    start: function () {
        this._super();
    },

    on_open_caller: function (event) {
        event.stopPropagation();
        var self = this;
        self._rpc({
            model: 'asterisk.server',
            method: 'get_record_from_my_channel',
            args: []
        }).then(function(r) {
        console.log('RESULT RPC r='+r);
        console.log('RESULT RPC type r='+typeof r);
        console.log('RESULT RPC isNaN r='+isNaN(r));
        if (r === false) {
             self.do_warn(
                _t('Failure'),
                _t('Problem in the connection to Asterisk'),
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
            self.do_notify(
                _t('Success'),
                _.str.sprintf(_t('Moving to %s ID %d'), r[0], r[1]),
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

SystrayMenu.Items.push(click2dialOpenCaller);

});
