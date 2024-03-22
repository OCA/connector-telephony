/*eslint-disable*/
odoo.define(
    "connector_phone_cloudcti_event_manager.connector_phone_cloudcti_event_manager",
    function(require) {
        "use strict";

        var basic_fields = require("web.basic_fields");
        var Notification = require("web.Notification");
        var WebClient = require("web.WebClient");

        var OutGoingNotification = Notification.extend({
            template: "OutGoingNotification",

            init: function(parent, params) {
                this._super(parent, params);
                this.eid = params.eventID;
                this.sticky = false;

                this.events = _.extend(this.events || {}, {
                    "click .link2event": function() {
                        var self = this;
                        this._rpc({
                            model: "res.partner",
                            method: "cloudcti_outgoing_call_notification",
                            args: [[this.eid]],
                        }).then(function() {
                            self.close();
                        });
                    },
                    "click .link2recall": function() {
                        this.close();
                    },
                });
            },
        });

        basic_fields.FieldPhone.include({
            _renderReadonly: function() {
                var self = this;
                this.$el.text(this.value).addClass("o_form_uri");
                this.$el.attr("href", "javascript:void(0)");
                this.$el.click(function() {
                    var title =
                        "Outgoing call :" + self.recordData.display_name + self.value;
                    var message =
                        "Name :" +
                        self.recordData.display_name +
                        "<br/> Phone:" +
                        self.value;
                    self.call("notification", "notify", {
                        Notification: OutGoingNotification,
                        title: title,
                        message: message,
                        eventID: self.recordData.id,
                    });
                });
            },
        });

        var IncomingNotification = Notification.extend({
            template: "IncomingNotification",

            init: function(parent, params) {
                console.log("?/////paramsparams///////////////", params) 
                this._super(parent, params);
                this.eid = params.eventID;
                this.sticky = false;

                this.events = _.extend(this.events || {}, {
                    "click .link2event": function() {
                        var self = this;
                        this._rpc({
                            model: "res.partner",
                            method: "incoming_call_notification",
                            args: [this.eid],
                        }).then(function(r) {
                            // Alert("Done",)
                            self.do_action(r);
                            self.close();
                        });
                    },
                    "click .link2recall": function() {
                        this.close();
                    },
                });
            },
        });

        WebClient.include({
            on_message: function(message) {
                if (message.notification) {
                    return this.call("notification", "notify", {
                        Notification: IncomingNotification,
                        title: message.title,
                        message: message.message,
                        sticky: message.sticky,
                        className: message.className,
                        eventID: message.id,
                    });
                }
                if (message.Outnotification) {
                    return this.call("notification", "notify", {
                        Notification: OutGoingNotification,
                        title: message.title,
                        message: message.message,
                        sticky: message.sticky,
                        className: message.className,
                        eventID: message.id,
                    });
                }
                return this.call("notification", "notify", {
                    type: message.type,
                    title: message.title,
                    message: message.message,
                    sticky: message.sticky,
                    className: message.className,
                });
            },
        });

        return {
            OutGoingNotification: OutGoingNotification,
        };
    }
);
