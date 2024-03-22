/** @odoo-module **/

import {markup} from "@odoo/owl";
import {browser} from "@web/core/browser/browser";
import {registry} from "@web/core/registry";
import {_t} from "@web/core/l10n/translation";

export const webNotificationCloudCtiService = {
    dependencies: ["bus_service", "notification"],

    start(env, {bus_service, notification}) {
        let webNotifTimeouts = {};
        function displaywebNotification(notifications) {
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
                                name: _t("Refresh"),
                                primary: true,
                                onClick: () => {
                                    browser.location.reload();
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
                console.log("?///////////////////", type, notifications);
                if (type === "web.notify.custom") {
                    displaywebNotification(payload);
                }
            }
        });
        bus_service.start();
    },
};

registry
    .category("services")
    .add("webNotificationCloudCti", webNotificationCloudCtiService);

// Bus_service.addEventListener("notification", ({detail: notifications}) => {
//     for (const {payload, type} of notifications) {
//         console.log("?///////////////////", type, notifications)
//         if (type === "web.notify.incoming") {
//             displaywebNotification(payload);
//         }
//         else if (type === "web.notify.outgoing") {
//             displaywebNotification(payload);
//         }
//     }
// });
