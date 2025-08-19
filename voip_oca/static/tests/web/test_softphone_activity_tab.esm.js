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

QUnit.module("Softphone > Activity Tab");

QUnit.test("Check Activities", async () => {
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
    const [activityTypeId] = pyEnv["mail.activity.type"].search([
        ["category", "=", "phonecall"],
    ]);
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
    pyEnv["mail.activity"].create([
        {
            activity_type_id: activityTypeId,
            date_deadline: "2025-01-01",
            res_id: partnerId1,
            res_model: "res.partner",
            user_id: pyEnv.currentUserId,
            main_partner_id: partnerId1,
            activity_category: "phonecall",
        },
        {
            activity_type_id: activityTypeId,
            date_deadline: "2025-02-01",
            res_id: partnerId2,
            res_model: "res.partner",
            user_id: pyEnv.currentUserId,
            main_partner_id: partnerId2,
            activity_category: "phonecall",
        },
    ]);
    start();
    await contains(".o_menu_systray .o_nav_entry[title='Softphone']");
    await click(".o_menu_systray .o_nav_entry[title='Softphone']");
    await contains(".o_voip_softphone");
    await click(".o_voip_softphone li a[name='activity_list']");
    await contains(".o_voip_softphone .o_voip_activity_item", {count: 2});
    await click(".o_voip_softphone .o_voip_activity_item", {text: "Test Partner"});
    await contains(".o_voip_softphone .o_voip_partner_header");
    await contains(".o_voip_softphone .o_voip_partner_actions");
    await contains(".o_voip_softphone .o_voip_partner_activity");
});
