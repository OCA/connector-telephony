/*
    Copyright 2025 Dixmit
    License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
*/
import {Component, onMounted, useRef, useState} from "@odoo/owl";
import {useSelection} from "@mail/utils/common/hooks";
import {useService} from "@web/core/utils/hooks";

export class Numpad extends Component {
    setup() {
        super.setup();
        this.keys = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "*", "0", "#"];
        this.voip = useState(useService("voip_oca"));
        this.numpadValue = useRef("numpadValue");
        this.selectionNumpad = useSelection({
            refName: "numpadValue",
            model: this.voip.numpad.selection,
        });
        onMounted(() => this.numpadValue.el.focus());
    }

    onKeyClick(key) {
        const {value} = this.voip.numpad;
        const {selectionStart, selectionEnd} = this.numpadValue.el;
        this.voip.numpad.value =
            value.slice(0, selectionStart) + key + value.slice(selectionEnd);
        this.numpadValue.el.focus();
        this.selectionNumpad.restore();
        this.onNumpadValue({key});
    }

    onNumpadValue(ev) {
        const {value} = this.voip.numpad;
        if (ev.key === "Enter" && value.length > 0) {
            this.props.onCall();
            return;
        }
        this.props.onNumpadValue(ev.key);
    }

    deleteNumber() {
        const {value} = this.voip.numpad;
        if (value.length > 0) {
            this.voip.numpad.value = value.slice(0, -1);
        }
    }
}
Numpad.props = {
    onNumpadValue: {type: Function, optional: true},
    onCall: {type: Function, optional: true},
};
Numpad.defaultProps = {
    // eslint-disable-next-line no-empty-function
    onNumpadValue: () => {},
    // eslint-disable-next-line no-empty-function
    onCall: () => {},
};
Numpad.template = "voip_oca.Numpad";
