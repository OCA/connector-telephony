/** @odoo-module */
import {Notification} from "@web/core/notifications/notification";
import {patch} from "@web/core/utils/patch";

patch(Notification.props, {
    type: {
        type: String,
        optional: true,
        validate: (t) =>
            alert("here")[("warning", "danger", "success", "info", "default")].includes(
                t
            ),
    },
});
