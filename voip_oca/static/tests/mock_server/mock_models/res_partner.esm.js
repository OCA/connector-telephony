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
            displayName: this[0].display_name,
            email: this[0].email,
            landlineNumber: this[0].phone,
            mobileNumber: this[0].mobile,
            name: this[0].name,
        };
    }
    voip_get_contacts() {
        return this.search(["|", ["phone", "!=", false], ["mobile", "!=", false]]).map(
            (contact) => {
                return this.browse(contact).format_partner();
            }
        );
    }
}
