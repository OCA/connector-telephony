/** @odoo-module */
/* global QUnit */
/*
    Copyright 2025 Dixmit
    License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
*/

import {click, contains} from "@web/../tests/utils";
import {start} from "@mail/../tests/helpers/test_utils";

QUnit.module("Softphone");

QUnit.test("Click on softphone hides the information", async () => {
    start();
    await contains(".o_menu_systray .o_nav_entry[title='Softphone']");
    await click(".o_menu_systray .o_nav_entry[title='Softphone']");
    await contains(".o_voip_softphone");
    await contains(".o_voip_softphone .o_voip_softphone_content");
    await contains(".o_voip_softphone .o_voip_softphone_header");
    await click(".o_voip_softphone .o_voip_softphone_header");
    await contains(".o_voip_softphone");
    await contains(".o_voip_softphone .o_voip_softphone_header");
    await contains(".o_voip_softphone .o_voip_softphone_content", {count: 0});
});
