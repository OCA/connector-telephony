/** @odoo-module **/

/*
    Copyright 2024 Dixmit
    License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
*/

import {Component} from "@odoo/owl";
import {_t} from "@web/core/l10n/translation";
import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";

const systrayRegistry = registry.category("systray");

export class Click2DialSystray extends Component {
    setup() {
        this.rpc = useService("rpc");
        this.action = useService("action");
        this.notification = useService("notification");
        this.user = useService("user");
    }

    async onOpenCaller() {
        // Var session = require('web.session');

        const r = await this.rpc("/asterisk_click2dial/get_record_from_my_channel", {
            context: this.user.context,
        });
        if (r === false) {
            this.notification.add(
                _t(
                    "Calling party number not retreived from IPBX or IPBX unreachable by Odoo"
                ),
                {
                    title: _t("IPBX error"),
                }
            );
        } else if (typeof r === "string" && isNaN(r)) {
            this.notification.add(_t("The calling number is not a phone number!"), {
                title: r,
            });
        } else if (typeof r === "string") {
            var action = {
                name: _t("Number Not Found"),
                type: "ir.actions.act_window",
                res_model: "number.not.found",
                view_mode: "form",
                views: [[false, "form"]],
                target: "new",
                context: {default_calling_number: r},
            };
            this.action.doAction(action);
        } else if (typeof r === "object" && r.length === 3) {
            this.notification.add(
                _t("Moving to form view of %s (%s ID %s)", r[2], r[0], r[1]),
                {
                    title: _t("On the phone with '%s'", r[2]),
                }
            );
            var action_suc = {
                type: "ir.actions.act_window",
                res_model: r[0],
                res_id: r[1],
                view_mode: "form,tree",
                views: [[false, "form"]],
                /* If you want to make it work with the 'web' module
        of Odoo Enterprise edition, you have to change the line
        target: 'current',
            to:
        target: 'new',
        If you want to use target: 'current', with web/enterprise,
        you have to reload the Web page just after */
                target: "current",
                context: {},
            };
            this.action.doAction(action_suc);
        }
    }
}

Click2DialSystray.template = "asterisk_click2dial.Click2DialSystray";

export const systrayItem = {Component: Click2DialSystray};

systrayRegistry.add("asterisk_click2dial.Click2DialSystray", systrayItem, {
    sequence: 99,
});
