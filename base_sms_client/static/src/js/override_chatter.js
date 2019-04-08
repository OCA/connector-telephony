odoo.define('mail.Chatter.sms', function (require) {
    "use strict";

    var chatter = require('mail.Chatter');
    var bus = require('bus.bus').bus;

    chatter.include({

        events: _.extend({}, chatter.prototype.events, {
            'click .o_chatter_button_send_sms': '_onSendSMS',
        }),

        start: function() {
            this._super.apply(this, arguments);
            var channel = 'wizard.mass.sms';
            bus.add_channel(channel);
            bus.on('notification', this, function () {
                var self = this;
                self.trigger_up('reload');
            });
        },

        /**
         * Performs the action to open the SMS window.
         *
         * @private
         */
        _onSendSMS: function () {
            var self = this
            this._rpc({
                model: 'wizard.mass.sms',
                method: 'redirect_to_sms_wizard',
                args: [[]],
                kwargs: {
                    'id':this.record.res_id,
                    'model':this.record.model,
                },
                context: this.record.getContext(),
            }).then(function (result) {
                self.do_action(result, {
                    additional_context: {
                        'active_ids': [self.record.res_id],
                        'active_id': [self.record.res_id],
                        'active_model': self.record.model,
                    },
                })
            });
        },
    });
});
