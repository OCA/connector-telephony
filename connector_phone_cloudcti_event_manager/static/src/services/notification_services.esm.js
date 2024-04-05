/** @odoo-module **/

import {markup} from "@odoo/owl";
import {browser} from "@web/core/browser/browser";
import {registry} from "@web/core/registry";
import {_t} from "@web/core/l10n/translation";
import {useService} from "@web/core/utils/hooks";

export const webNotificationCloudCtiService = {
    dependencies: ["bus_service", "notification", "orm", "action"],

    start(env, {bus_service, notification, orm, action}) {
        let webNotifTimeouts = {};

        function displaywebNotification(notifications, method, name) {
            Object.values(webNotifTimeouts).forEach((notif) =>
                browser.clearTimeout(notif)
            );
            webNotifTimeouts = {};

            notifications.forEach(function (notif) {
                browser.setTimeout(function () {
                    notification.add(markup(notif.message), {
                        title: notif.title,
                        type: notif.type,
                        sticky: notif.sticky,
                        className: notif.className,
                        buttons: [
                            {
                                name: _t(name),
                                primary: true,
                                onClick: async () => {
                                    if (name == "Ok") {
                                        this.close();
                                        browser.location.reload();
                                        return;
                                    }
                                    this.eid = notif.target;
                                    var self = this;
                                    if (method == "incoming_call_notification") {
                                        await orm
                                            .call("res.partner", method, [this.eid])
                                            .then(function (data) {
                                                action.doAction(data);
                                                self.close();
                                            });
                                    }
                                    if (
                                        method == "cloudcti_outgoing_call_notification"
                                    ) {
                                        await orm
                                            .call("res.partner", method, [this.eid])
                                            .then(() => {
                                                self.close();
                                            });
                                    }
                                },
                            },
                            {
                                name: _t("Close"),
                                primary: true,
                                onClick: () => {
                                    browser.location.reload();
                                },
                            },
                        ],
                    });
                });
            });
        }

        bus_service.addEventListener("notification", ({detail: notifications}) => {
            for (const {payload, type} of notifications) {
                if (type === "web.notify.incoming") {
                    var method = "incoming_call_notification";
                    var name = "Open Contact";
                    payload[0].title = "Incoming Call";
                    payload[0].message = "";
                    displaywebNotification(payload, method, name);
                }
                if (type === "web.notify.outgoing") {
                    var name = "Ok";
                    var method = "cloudcti_outgoing_call_notification";
                    displaywebNotification(payload, method, name);
                }
            }
        });
        bus_service.start();
    },
};

registry
    .category("services")
    .add("webNotificationCloudCti", webNotificationCloudCtiService);
