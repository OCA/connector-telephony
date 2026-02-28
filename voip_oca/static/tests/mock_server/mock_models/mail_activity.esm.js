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
        return this.activity_format(items);
    }

    _to_store(store) {
        super._to_store(...arguments);
        for (const activity of this) {
            if (activity.main_partner_id) {
                store._add_record_fields(this.browse(activity.id), {
                    main_partner_id: activity.main_partner_id,
                });
            }
            if (activity.main_partner) {
                store._add_record_fields(this.browse(activity.id), {
                    main_partner: activity.main_partner,
                });
            }
        }
    }
}
