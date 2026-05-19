/*
    Copyright 2025 Dixmit
    License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
*/
import {click, start, startServer} from "@mail/../tests/mail_test_helpers";
import {expect, test} from "@odoo/hoot";
import {animationFrame} from "@odoo/hoot-dom";
import {defineVoipModels} from "../voip_test_helpers.esm";
import {patchWithCleanup} from "@web/../tests/web_test_helpers";
import {session} from "@web/session";

// As we use mail as a dependancy, we need to declare models.
defineVoipModels();

test("Check Activity Tab", async () => {
    const pyEnv = await startServer();
    const partnerId = pyEnv["res.partner"].create({
        name: "Test Partner",
        display_name: "Test Partner",
        phone: "123456789",
    });
    const activityTypeId = pyEnv["mail.activity.type"].create({
        name: "Call",
        category: "phonecall",
    });
    pyEnv["mail.activity"].create({
        res_id: partnerId,
        res_model: "res.partner",
        user_id: pyEnv.user.id,
        main_partner_id: partnerId,
        main_partner: "Test Partner",
        activity_category: "phonecall",
        activity_type_id: activityTypeId.id,
    });
    patchWithCleanup(session, {
        ...session,
        voip: {pbx_id: 1},
    });
    await start();
    expect(".o_menu_systray .o_nav_entry[title='Softphone']").toHaveCount(1);
    click(".o_menu_systray .o_nav_entry[title='Softphone']");
    await animationFrame();
    expect(".o_voip_softphone").toHaveCount(1);
    click(".o_voip_softphone li a[name='activity_list']");
    await animationFrame();
    expect(".o_voip_softphone .o_voip_activity_item").toHaveCount(1);
    click(".o_voip_softphone .o_voip_activity_item", {text: "Test Partner"});
    await animationFrame();
    expect(".o_voip_softphone .o_voip_partner_header").toHaveCount(1);
    expect(".o_voip_softphone .o_voip_partner_actions").toHaveCount(1);
    expect(".o_voip_softphone .o_voip_partner_activity").toHaveCount(1);
});
