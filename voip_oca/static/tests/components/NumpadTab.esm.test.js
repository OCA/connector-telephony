/*
    Copyright 2025 Dixmit
    License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
*/
import {click, start} from "@mail/../tests/mail_test_helpers";
import {expect, test} from "@odoo/hoot";
import {animationFrame} from "@odoo/hoot-dom";

import {defineVoipModels} from "../voip_test_helpers.esm";
import {patchWithCleanup} from "@web/../tests/web_test_helpers";
import {session} from "@web/session";

// As we use mail as a dependancy, we need to declare models.
defineVoipModels();

test("Check Numpad Tab", async () => {
    patchWithCleanup(session, {
        ...session,
        voip: {pbx_id: 1},
    });
    await start();
    expect(".o_menu_systray .o_nav_entry[title='Softphone']").toHaveCount(1);
    click(".o_menu_systray .o_nav_entry[title='Softphone']");
    await animationFrame();
    expect(".o_voip_softphone").toHaveCount(1);
    click(".o_voip_softphone .o_voip_softphone_footer button[title='Open Numpad']");
    await animationFrame();
    expect(".o_voip_softphone .o_numpad_input").toHaveCount(1);
    expect(".o_voip_softphone .o_numpad_input").toHaveValue("");
    expect(".o_voip_softphone .o_numpad_button").toHaveCount(12);
    click(".o_voip_softphone .o_numpad_button", {text: "1"});
    await animationFrame();
    expect(".o_voip_softphone .o_numpad_input").toHaveValue("1");
    click(".o_voip_softphone .o_numpad_button", {text: "2"});
    await animationFrame();
    expect(".o_voip_softphone .o_numpad_input").toHaveValue("12");
    click(".o_voip_softphone .o_numpad_delete");
    await animationFrame();
    expect(".o_voip_softphone .o_numpad_input").toHaveValue("1");
});
