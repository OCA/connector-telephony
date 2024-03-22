/** @odoo-module **/

import { Notification } from "@web/core/notifications/notification";
import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";

// patch(Notification.props ,{
//     setup() {
//         onWillStart(async () => {
//             var self = this;
//             alert("..........vt")
//             var gettime = this._rpc({
//                 model: 'res.company',
//                 method: 'get_popup_time',
//                 args: [[session.company_id]],
//             }).then(function (time) {
//                 self._autoCloseDelay = time && time * 1000 || 2500
//             });
//             return $.when(
//                 gettime,
//                 this._super.apply(this, arguments)
//             );
//         })
//     }
// })
