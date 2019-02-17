odoo.define('base_phone_popup', function (require) {
'use strict';

    var core = require('web.core');
    var web_client = require('web.WebClient');
    var Widget = require('web.Widget');
    var bus = require('bus.bus').bus;
//    var session = require('web.session');
    var base_phone_popup = odoo.base_phone_popup = {};

    base_phone_popup.Request = Widget.extend({
        init: function(parent, user_id) {
            var self = this;
            this._super(parent);
            this.uid = this.getSession().uid
            this.bus = bus;
            this.channel = 'bpp_' + this.uid;
            this.bus.add_channel(this.channel);
            this.bus.on("notification", this, this.on_notification);
            this.bus.start_polling();
            console.log('Request.init  channel -> ' + this.channel);
        },
        on_notification: function(notification) {
            var self = this;
            var channel = notification[0][0];
            var action = notification[0][1];
            console.log("channel -> " + JSON.stringify(channel) + "     action -> " + JSON.stringify(action));
            if (channel == this.channel) {
                this.do_action(action);
            }
        },
    });
    web_client.include({
        show_application: function() {
            this._super();
            console.log(" Show_application   uid -> " + this.getSession().uid);
            this.base_phone_popup = new base_phone_popup.Request(this, this.getSession().uid);
        },
    });
});
