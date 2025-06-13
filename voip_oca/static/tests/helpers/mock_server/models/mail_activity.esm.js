/* @odoo-module */
/*
    Copyright 2025 Dixmit
    License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
*/
// Ensure mail overrides are applied first
import "@mail/../tests/helpers/mock_server/models/mail_activity";

import {serializeDate, today} from "@web/core/l10n/dates";
import {MockServer} from "@web/../tests/helpers/mock_server";
import {patch} from "@web/core/utils/patch";

patch(MockServer.prototype, {
    /**
     * @override
     */
    async _performRPC(_route, {model, method, args, kwargs}) {
        if (model !== "mail.activity") {
            return super._performRPC(...arguments);
        }
        switch (method) {
            case "get_call_activities":
                return this._mockGetCallActivities(...args, kwargs);
            default:
                return super._performRPC(...arguments);
        }
    },
    _mockGetCallActivities() {
        const activityTypeIds = this.pyEnv["mail.activity.type"].search([
            ["category", "=", "phonecall"],
        ]);
        return this._mockMailActivityActivityFormat(
            this.getRecords("mail.activity", [
                ["activity_type_id", "in", activityTypeIds],
                ["user_id", "=", this.pyEnv.currentUserId],
                ["date_deadline", "<=", serializeDate(today())],
            ]).map((record) => record.id)
        );
    },
});
