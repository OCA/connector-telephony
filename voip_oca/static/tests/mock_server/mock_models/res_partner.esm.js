/*
    Copyright 2025 Dixmit
    License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
*/
import {mailModels} from "@mail/../tests/mail_test_helpers";

export class ResPartner extends mailModels.ResPartner {
    format_partner() {
        return {
            id: this[0].id,
            type: "partner",
            display_name: this[0].display_name,
            email: this[0].email,
            phone: this[0].phone,
            name: this[0].name,
        };
    }
    voip_get_contacts() {
        var result = [];
        for (const contact of this.search([["phone", "!=", false]])) {
            result.push(this.browse(contact).format_partner());
        }
        return {"res.partner": result};
    }
}
