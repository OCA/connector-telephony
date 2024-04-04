/** @odoo-module **/

/*
    Copyright 2024 Dixmit
    License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
*/

import {Component} from "@odoo/owl";
import {_t} from "@web/core/l10n/translation";
import {useService} from "@web/core/utils/hooks";

export class OnDialButton extends Component {
    setup() {
        this.notification = useService("notification");
        this.title = _t("Dial phone");
        this.orm = useService("orm");
    }
    async onClick() {
        await this.props.record.save();
        this.click2dial(this.props.record.data[this.props.name].replace(/\s+/g, ""));
    }
    click2dial(phone_num) {
        var self = this;
        this.notification.add(_t("Unhook your ringing phone"), {
            title: _t("Click2dial to %s", phone_num),
        });
        var params = {
            phone_number: phone_num,
            click2dial_model: this.model,
            click2dial_id: this.res_id,
        };
        return this.orm
            .call("phone.common", "click2dial", [phone_num], {
                context: params,
            })
            .then(
                function (r) {
                    if (r === false) {
                        self.notification.add("Click2dial failed", {
                            type: "danger",
                        });
                    } else if (typeof r === "object") {
                        self.notification.add(
                            _t("Number dialed: %s", r.dialed_number),
                            {
                                title: _t("Click2dial successfull"),
                            }
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
                function () {
                    self.notification.add("Click2dial failed", {
                        type: "danger",
                    });
                }
            );
    }
}
OnDialButton.template = "base_phone.OnDialButton";
OnDialButton.props = ["*"];
