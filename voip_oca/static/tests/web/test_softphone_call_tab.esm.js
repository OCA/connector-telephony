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

QUnit.module("Softphone > Call Tab");

QUnit.test("Check Call", async () => {
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
    const [partnerId1, partnerId2] = pyEnv["res.partner"].create([
        {
            name: "Test Partner",
            mobile: "+34 666 666 666",
        },
        {
            name: "Other Test Partner",
            phone: "777 777",
        },
    ]);
    pyEnv["voip.call"].create([
        {
            name: "Test Partner",
            phone_number: "+34 666 666 666",
            state: "terminated",
            pbx_id: pbxId,
            partner_id: partnerId1,
            user_id: pyEnv.currentUserId,
            start_date: "2016-12-11 05:15:00",
            end_date: "2016-12-11 05:30:00",
            create_date: "2016-12-11 05:15:00",
        },
        {
            name: "Other Test Partner",
            phone_number: "777 777",
            state: "terminated",
            pbx_id: pbxId,
            partner_id: partnerId2,
            user_id: pyEnv.currentUserId,
            start_date: "2016-12-11 05:15:00",
            end_date: "2016-12-11 05:30:00",
            create_date: "2016-12-11 05:15:00",
        },
    ]);
    start();
    await contains(".o_menu_systray .o_nav_entry[title='Softphone']");
    await click(".o_menu_systray .o_nav_entry[title='Softphone']");
    await contains(".o_voip_softphone");
    await click(".o_voip_softphone li a[name='call_list']");
    await contains(".o_voip_softphone .o_voip_call_item", {count: 2});
    await click(".o_voip_softphone .o_voip_call_item", {text: "Test Partner"});
    await contains(".o_voip_softphone .o_voip_partner_header");
    await contains(".o_voip_softphone .o_voip_partner_actions");
    await contains(".o_voip_softphone .o_voip_partner_activity", {count: 0});
});
