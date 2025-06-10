/*
    Copyright 2025 Dixmit
    License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
*/
import {fields, models} from "@web/../tests/web_test_helpers";

export class VoipOcaCall extends models.ServerModel {
    _name = "voip.call";

    phone_number = fields.Char();
    name = fields.Char();
    type_call = fields.Selection({
        selection: [
            ["incoming", "Incoming"],
            ["outgoing", "Outgoing"],
        ],
        default: "incoming",
    });
    state = fields.Selection({
        selection: [
            ["draft", "Draft"],
            ["in_progress", "In Progress"],
            ["done", "Done"],
            ["cancelled", "Cancelled"],
        ],
        default: "draft",
    });
    duration = fields.Integer({
        string: "Duration",
        default: 0,
    });
    pbx_id = fields.Many2one({
        relation: "voip.pbx",
        required: true,
    });
    partner_id = fields.Many2one({
        relation: "res.partner",
    });
    user_id = fields.Many2one({
        relation: "res.users",
        required: true,
    });
    start_date = fields.Datetime();
    end_date = fields.Datetime();

    get_recent_calls() {
        return this.search([["user_id", "=", this.env.user.id]]).map((item) =>
            this.browse(item).format_call()
        );
    }
    format_call() {
        return {
            id: this[0].id,
            creationDate: this[0].create_date,
            typeCall: this[0].type_call,
            displayName: this[0].display_name,
            endDate: this[0].end_date,
            partner:
                this[0].partner_id &&
                this.env["res.partner"].browse(this[0].partner_id).format_partner(),
            phoneNumber: this[0].phone_number,
            startDate: this[0].start_date,
            createDate: this[0].create_date,
            state: this[0].state,
        };
    }
}
