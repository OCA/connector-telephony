/** @odoo-module */
/* global QUnit */
/*
    Copyright 2025 Dixmit
    License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
*/

import {click, contains} from "@web/../tests/utils";
import {nextTick, patchWithCleanup} from "@web/../tests/helpers/utils";
import {start} from "@mail/../tests/helpers/test_utils";
import {startServer} from "@bus/../tests/helpers/mock_python_environment";
import {session} from "@web/session";

QUnit.module("Softphone Numpad");

QUnit.test("Click on numpad and numpad buttons", async () => {
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
    await click(
        ".o_voip_softphone .o_voip_softphone_footer button[title='Open Numpad']"
    );
    await contains(".o_voip_softphone .o_numpad_input");
    await contains(".o_voip_softphone .o_numpad_input", {value: ""});
    await contains(".o_voip_softphone .o_numpad_button", {count: 12});
    await click(".o_voip_softphone .o_numpad_button", {text: "1"});
    await nextTick();
    await click(".o_voip_softphone .o_numpad_button", {text: "2"});
    await nextTick();
    await contains(".o_voip_softphone .o_numpad_input", {value: "12"});
    await click(".o_voip_softphone .o_numpad_delete");
    await nextTick();
    await contains(".o_voip_softphone .o_numpad_input", {value: "1"});
});
