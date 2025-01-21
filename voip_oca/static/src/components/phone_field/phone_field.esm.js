/** @odoo-module **/
/*
    Copyright 2025 Dixmit
    License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
*/
import {PhoneField} from "@web/views/fields/phone/phone_field";
import {patch} from "@web/core/utils/patch";
import {useService} from "@web/core/utils/hooks";

patch(PhoneField.prototype, {
    setup() {
        super.setup();
        this.agent = useService("voip_agent_oca");
    },
    onPhoneClick(ev) {
        if (!this.agent.agent) {
            return;
        }
        ev.preventDefault();
        ev.stopPropagation();
        console.log(this.props.record, this.props.name);
        this.agent.call({number: this.props.record.data[this.props.name]});
    },
});
