/* Base phone module for Odoo
   Copyright (C) 2013-2018 Akretion France
   @author: Alexis de Lattre <alexis.delattre@akretion.com>
   License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */

odoo.define("base_phone.updatedphone_widget", function(require) {
    "use strict";

    var core = require("web.core");
    var FieldPhone = require("web.basic_fields").FieldPhone;
    var _t = core._t;

    FieldPhone.include({
        /* Always enable phone link tel:, not only on small screens  */
        _canCall: function() {
            return true;
        },
        showDialButton: function() {
            // Must be inherited by ipbx specific modules
            // and set to true
            return false;
        },

        _renderReadonly: function() {
            // Create a link to trigger action on server
            // this link will be after the <a href="tel:">
            this._super();

            if (!this.showDialButton()) {
                return;
            }
            var self = this;

            // Create our link
            var dial = $(
                '<a href="#" class="dial"><div class="label label-primary">☎ Dial</div></a>'
            );

            // Add a parent element
            // it's not possible to append to $el directly
            // because $el don't have any parent yet
            var parent = $("<div>");
            parent.append([this.$el[0], " ", dial]);

            // Replace this.$el by our new container
            this.$el = parent;

            var phone_num = this.value;
            dial.click(function(evt) {
                self.click2dial(phone_num);
            });
        },
        click2dial: function(phone_num) {
            var self = this;
            this.do_notify(
                _.str.sprintf(_t("Click2dial to %s"), phone_num),
                _t("Unhook your ringing phone"),
                false
            );
            var params = {
                phone_number: phone_num,
                click2dial_model: this.model,
                click2dial_id: this.res_id,
            };
            return this._rpc({
                model: "phone.common",
                context: params,
                method: "click2dial",
                args: [phone_num],
            }).then(
                function(r) {
                    console.log("successfull", r);
                    if (r === false) {
                        self.do_warn("Click2dial failed");
                    } else if (typeof r === "object") {
                        self.do_notify(
                            _t("Click2dial successfull"),
                            _.str.sprintf(_t("Number dialed: %s"), r.dialed_number),
                            false
                        );
                        if (r.action_model) {
                            var action = {
                                name: r.action_name,
                                type: "ir.actions.act_window",
                                res_model: r.action_model,
                                view_mode: "form",
                                views: [[false, "form"]],
                                target: "new",
                                context: params,
                            };
                            return self.do_action(action);
                        }
                    }
                },
                function(r) {
                    console.log("on error");
                    self.do_warn("Click2dial failed");
                }
            );
        },
    });

    return {
        FieldPhone: FieldPhone,
    };
});
