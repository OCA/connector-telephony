/** @odoo-module */
/* global QUnit */
/*
    Copyright 2025 Dixmit
    License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
*/

import {click, contains} from "@web/../tests/utils";
import {nextTick} from "@web/../tests/helpers/utils";
import {start} from "@mail/../tests/helpers/test_utils";

QUnit.module("Softphone Numpad");

QUnit.test("Click on numpad and numpad buttons", async () => {
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
