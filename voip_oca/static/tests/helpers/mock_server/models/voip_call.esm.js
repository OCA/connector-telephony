/* @odoo-module */
/*
    Copyright 2025 Dixmit
    License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
*/

import {MockServer} from "@web/../tests/helpers/mock_server";
import {patch} from "@web/core/utils/patch";

patch(MockServer.prototype, {
    /**
     * @override
     */
    async _performRPC(_route, {model, method, args, kwargs}) {
        if (model !== "voip.call") {
            return super._performRPC(...arguments);
        }
        switch (method) {
            case "get_recent_calls":
                return this._mockVoipOcaCall_GetRecentCalls(...args, kwargs);
            case "format_call":
                return this._mockVoipOcaCall_FormatCall(...args, kwargs);
            default:
                return super._performRPC(...arguments);
        }
    },
    _mockVoipOcaCall_FormatCall(ids) {
        const res = this.mockRead("voip.call", [ids])[0];
        return {
            id: res.id,
            creationDate: res.create_date,
            typeCall: res.type_call,
            displayName: res.display_name,
            endDate: res.end_date,
            partner:
                res.partner_id && this._mockResPartner_FormatPartner([res.partner_id]),
            phoneNumber: res.phone_number,
            startDate: res.start_date,
            createDate: res.create_date,
            state: res.state,
        };
    },
    _mockVoipOcaCall_GetRecentCalls() {
        return this.getRecords("voip.call", []).map((record) =>
            this._mockVoipOcaCall_FormatCall(record.id)
        );
    },
});
