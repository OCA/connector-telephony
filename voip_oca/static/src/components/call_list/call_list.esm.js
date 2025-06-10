/*
    Copyright 2025 Dixmit
    License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
*/

import {Component, onMounted} from "@odoo/owl";
import {_t} from "@web/core/l10n/translation";
import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";

export class CallList extends Component {
    setup() {
        super.setup();
        this.voip = useService("voip_oca");
        onMounted(() => this.voip.searchCalls());
    }

    onClick(call) {
        this.voip.open({call: call});
    }
}
CallList.props = {records: {type: Array}};
CallList.template = "voip_oca.CallList";

registry.category("voip_elements").add("call_list", {
    component: CallList,
    order: 10,
    title: _t("Calls"),
    input: "calls",
    search: (voip, value) => voip.searchCalls(value),
    call: (voip) => {
        if (voip.calls) {
            voip.open({call: voip.calls[0], partner: voip.calls[0]});
        }
    },
});
