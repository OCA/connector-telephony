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

test("Check Call Tab", async () => {
    const pyEnv = await startServer();
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
            pbx_id: 1,
            partner_id: partnerId1,
            user_id: pyEnv.user.id,
            start_date: "2016-12-11 05:15:00",
            end_date: "2016-12-11 05:30:00",
            create_date: "2016-12-11 05:15:00",
        },
        {
            name: "Other Test Partner",
            phone_number: "777 777",
            state: "terminated",
            pbx_id: 1,
            partner_id: partnerId2,
            user_id: pyEnv.user.id,
            start_date: "2016-12-11 05:15:00",
            end_date: "2016-12-11 05:30:00",
            create_date: "2016-12-11 05:15:00",
        },
    ]);
    patchWithCleanup(session, {
        ...session,
        voip: {pbx_id: 1},
    });
    await start();
    expect(".o_menu_systray .o_nav_entry[title='Softphone']").toHaveCount(1);
    click(".o_menu_systray .o_nav_entry[title='Softphone']");
    await animationFrame();
    expect(".o_voip_softphone").toHaveCount(1);
    click(".o_voip_softphone li a[name='call_list']");
    await animationFrame();
    expect(".o_voip_softphone .o_voip_call_item").toHaveCount(2);
    click(".o_voip_softphone .o_voip_call_item", {text: "Test Partner"});
    await animationFrame();
    expect(".o_voip_softphone .o_voip_partner_header").toHaveCount(1);
    expect(".o_voip_softphone .o_voip_partner_actions").toHaveCount(1);
    expect(".o_voip_softphone .o_voip_partner_activity").toHaveCount(0);
});
