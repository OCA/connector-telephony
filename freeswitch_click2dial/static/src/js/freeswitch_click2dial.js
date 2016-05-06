/* FreeSWITCH_click2dial module for OpenERP
   Copyright (C) 2014 Alexis de Lattre <alexis@via.ecp.fr>
   The licence is in the file __openerp__.py */

openerp.freeswitch_click2dial = function (instance) {

    var _t = instance.web._t;

    instance.web.OpenCaller = instance.web.Widget.extend({
        template:'freeswitch_click2dial.OpenCaller',

        start: function () {
            this.$('button').on('click', this.on_open_caller);
            this._super();
        },

        on_open_caller: function (event) {
            event.stopPropagation();
            var self = this;
            self.rpc('/freeswitch_click2dial/get_record_from_my_channel', {}).done(function(r) {
            // console.log('RESULT RPC r='+r);
            // console.log('RESULT RPC type r='+typeof r);
            if (r === false) {
                 self.do_notify(
                    _t('Failure'),
                    _t('Problem in the connection to FreeSWITCH'));
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
                instance.client.action_manager.do_action(action);
 
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
                instance.client.action_manager.do_action(action);
            }
        });
       },
    });

    instance.web.UserMenu.include({
        do_update: function(){
            this._super.apply(this, arguments);
            this.update_promise.then(function() {
                var freeswitch_button = new instance.web.OpenCaller();
                freeswitch_button.appendTo(instance.webclient.$el.find('.oe_systray'));
            });
        },
    });

};


