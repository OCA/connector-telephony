import {Activity} from "@mail/core/common/activity_model";
import {patch} from "@web/core/utils/patch";
import {assignIn} from "@mail/utils/common/misc";

patch(Activity, {
    _insert(data) {
        const activity = super._insert(...arguments);
        assignIn(activity, data, ["main_partner_id", "main_partner"]);
        return activity;
    },
});
