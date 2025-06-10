/*
    Copyright 2025 Dixmit
    License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
*/

import {Component, onMounted} from "@odoo/owl";
import {_t} from "@web/core/l10n/translation";
import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";

export class ActivityList extends Component {
    setup() {
        super.setup();
        this.voip = useService("voip_oca");
        onMounted(() => this.voip.searchActivities());
    }

    onClick(activity) {
        this.voip.open({activity: activity});
    }
}
ActivityList.props = {records: {type: Array}};
ActivityList.template = "voip_oca.ActivityList";

registry.category("voip_elements").add("activity_list", {
    component: ActivityList,
    order: 20,
    title: _t("Activities"),
    input: "activities",
    search: (voip, value) => voip.searchActivities(value),
    call: (voip) => {
        if (voip.activities) {
            voip.open({activity: voip.activities[0]});
        }
    },
});
