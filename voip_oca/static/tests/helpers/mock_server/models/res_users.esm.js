/* @odoo-module */
/*
    Copyright 2025 Dixmit
    License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
*/

import {MockServer} from "@web/../tests/helpers/mock_server";
import {patch} from "@web/core/utils/patch";

patch(MockServer.prototype, {
    _mockResUsers_InitMessaging(ids) {
        const user = this.getRecords("res.users", [["id", "in", ids]])[0];
        const pbx = this.getRecords("voip.pbx", [["id", "in", user.voip_pbx_id]]);
        return {
            ...super._mockResUsers_InitMessaging(...arguments),
            voip: {
                pbx_id: pbx.length && pbx[0].id,
                pbx: pbx.length && pbx[0].name,
                pbx_domain: pbx.length && pbx[0].domain,
                pbx_ws: pbx.length && pbx[0].ws_server,
                mode:
                    (pbx.length &&
                        user.voip_username &&
                        user.voip_password &&
                        pbx[0].mode) ||
                    "test",
                pbx_username: user.voip_username,
                pbx_password: user.voip_password,
                tones: {
                    dialtone: "/voip_oca/static/audio/dialtone.mp3",
                    calltone: "/voip_oca/static/audio/calltone.mp3",
                    ringbacktone: "/voip_oca/static/audio/ringbacktone.mp3",
                },
            },
        };
    },
});
