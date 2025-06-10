/*
    Copyright 2025 Dixmit
    License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
*/
import {fields} from "@web/../tests/web_test_helpers";
import {mailModels} from "@mail/../tests/mail_test_helpers";

export class MailActivity extends mailModels.MailActivity {
    main_partner_id = fields.Many2one({
        relation: "res.partner",
        string: "Main Partner",
    });
    main_partner = fields.Char();
    async get_call_activities() {
        const items = this.search([["activity_category", "=", "phonecall"]]);
        return items.activity_format();
    }
}
