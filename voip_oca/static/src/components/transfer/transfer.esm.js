/** @odoo-module **/
/*
    Copyright 2025 Dixmit
    License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
*/

import {Component, onMounted, useRef, useState} from "@odoo/owl";

export class Transfer extends Component {
    setup() {
        this.inputRef = useRef("input");
        this.state = useState({value: ""});
        onMounted(() => this.inputRef.el.focus());
    }
    onKeydown(ev) {
        if (ev.key === "Escape") {
            this.props.close();
        }
        if (ev.key === "Enter") {
            this.transfer();
        }
    }
    transfer() {
        this.props.onTransfer(this.state.value);
        this.props.close();
    }
}
Transfer.template = "voip_oca.Transfer";
Transfer.props = {
    onTransfer: {type: Function},
    close: {type: Function},
};
