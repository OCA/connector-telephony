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

QUnit.module("Softphone > Partner Tab");

QUnit.test("Check Partner", async () => {
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
    pyEnv["res.partner"].create([
        {
            name: "Test Partner",
            mobile: "+34 666 666 666",
        },
        {
            name: "Other Test Partner",
            phone: "777 777",
        },
    ]);
    start();
    await contains(".o_menu_systray .o_nav_entry[title='Softphone']");
    await click(".o_menu_systray .o_nav_entry[title='Softphone']");
    await contains(".o_voip_softphone");
    await click(".o_voip_softphone li a[name='partner_list']");
    await contains(".o_voip_softphone .o_voip_partner_item", {count: 2});
    await click(".o_voip_softphone .o_voip_partner_item", {text: "Test Partner"});
    await contains(".o_voip_softphone .o_voip_partner_header");
    await contains(".o_voip_softphone .o_voip_partner_actions");
    await contains(".o_voip_softphone .o_voip_partner_activity", {count: 0});
});
