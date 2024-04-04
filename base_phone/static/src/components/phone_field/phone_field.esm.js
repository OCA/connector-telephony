/** @odoo-module **/

/*
    Copyright 2024 Dixmit
    License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
*/

import {OnDialButton} from "@base_phone/components/on_dial_button/on_dial_button.esm";
import {PhoneField} from "@web/views/fields/phone/phone_field";
import {patch} from "@web/core/utils/patch";

patch(PhoneField, {
    components: {
        ...PhoneField.components,
        OnDialButton,
    },
});
