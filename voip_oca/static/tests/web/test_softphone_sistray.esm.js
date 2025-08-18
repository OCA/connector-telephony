/** @odoo-module */
/* global QUnit */
/*
    Copyright 2025 Dixmit
    License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
*/

import {click, contains} from "@web/../tests/utils";
import {start} from "@mail/../tests/helpers/test_utils";
import {startServer} from "@bus/../tests/helpers/mock_python_environment";
import {patchWithCleanup} from "@web/../tests/helpers/utils";
import {session} from "@web/session";

QUnit.module("VOIP Systray");

QUnit.test("Click on systray softphone item", async () => {
    const pyEnv = await startServer();
    const pbxId = pyEnv["voip.pbx"].create([
        {
            name: "Test PBX",
            domain: "pbx.domain",
            ws_server: "wss://pbx.domain",
            mode: "test",
        },
    ]);
    patchWithCleanup(session, {
        ...session,
        voip: {pbx_id: pbxId},
    });
    start();
    await contains(".o_menu_systray .o_nav_entry[title='Softphone']");
    await click(".o_menu_systray .o_nav_entry[title='Softphone']");
    await contains(".o_voip_softphone");
});

QUnit.test(
    "Systray button is not displayed when no voip_pbx_id defined on user",
    async () => {
        patchWithCleanup(session, {
            ...session,
            voip: {pbx_id: false},
        });
        start();
        await contains(".o_avatar");
        await contains(".o_menu_systray .o_nav_entry[title='Softphone']", {count: 0});
    }
);
