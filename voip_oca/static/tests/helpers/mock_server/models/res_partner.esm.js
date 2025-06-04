/* @odoo-module */
/*
    Copyright 2025 Dixmit
    License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
*/

import {MockServer} from "@web/../tests/helpers/mock_server";
import {patch} from "@web/core/utils/patch";

patch(MockServer.prototype, {
    async _performRPC(_route, {model, method, args, kwargs}) {
        if (model !== "res.partner") {
            return super._performRPC(...arguments);
        }
        switch (method) {
            case "format_partner":
                return this._mockResPartner_FormatPartner(...args, kwargs);
            case "voip_get_contacts":
                return this._mockResPartner_GetVoipContacts(...args, kwargs);
            default:
                return super._performRPC(...arguments);
        }
    },
    _mockResPartner_FormatPartner(ids) {
        const res = this.mockRead("res.partner", ids)[0];
        return {
            id: res.id,
            type: "partner",
            displayName: res.display_name,
            email: res.email,
            landlineNumber: res.phone,
            mobileNumber: res.mobile,
            name: res.name,
        };
    },
    _mockResPartner_GetVoipContacts() {
        return this.getRecords("res.partner", [
            "|",
            ["phone", "!=", false],
            ["mobile", "!=", false],
        ]).map((record) => this._mockResPartner_FormatPartner([record.id]));
    },
});
