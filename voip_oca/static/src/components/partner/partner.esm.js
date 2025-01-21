/** @odoo-module **/
/*
    Copyright 2025 Dixmit
    License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
*/

import {Component} from "@odoo/owl";
import {useService} from "@web/core/utils/hooks";

export class Partner extends Component {
    setup() {
        super.setup();
        this.action = useService("action");
        this.voip = useService("voip_oca");
        this.agent = useService("voip_agent_oca");
        this.activityService = useService("mail.activity");
        this.threadService = useService("mail.thread");
    }
    get phoneNumber() {
        return (
            this.props.call.phoneNumber ||
            this.props.partner.mobileNumber ||
            this.props.partner.landlineNumber
        );
    }
    get model() {
        if (this.props.activity && this.props.activity.res_model) {
            return this.props.activity.res_model;
        }
        return "res.partner";
    }
    get resId() {
        if (this.props.activity && this.props.activity.id) {
            return this.props.activity.id;
        }
        return this.props.partner.id;
    }
    onClose() {
        this.voip.call = false;
        this.voip.activity = false;
        this.voip.partner = false;
    }
    onOpenDocument() {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: this.model,
            views: [[false, "form"]],
            target: "new",
            res_id: this.resId,
        });
    }
    onEmailClick() {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "mail.compose.message",
            views: [[false, "form"]],
            target: "new",
            context: {
                default_model: this.model,
                default_res_ids: this.resId ? [this.resId] : false,
                default_partner_ids: this.resId ? [this.resId] : false,
                default_composition_mode: "comment",
                default_use_template: true,
                default_subject: "Comment",
            },
        });
    }
    onOpenPartnerClick() {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "res.partner",
            views: [[false, "form"]],
            res_id: this.props.partner.id,
            target: "new",
        });
    }
    onNewPartnerClick() {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "res.partner",
            views: [[false, "form"]],
            target: "new",
            context: {
                default_phone: this.phoneNumber,
            },
        });
    }
    onScheduleActivity() {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "mail.activity",
            views: [[false, "form"]],
            target: "new",
            context: {
                default_res_id: this.resId,
                default_res_model: this.model,
            },
        });
    }
    onCall() {
        this.agent.call({number: this.phoneNumber, partner: this.props.partner});
    }
    async onMarkAsDone() {
        await this.activityService.markAsDone(this.props.activity);
        await this.threadService.fetchData(
            this.threadService.getThread(
                this.props.activity.res_model,
                this.props.activity.res_id
            ),
            ["activities"]
        );
        this.voip.call = false;
        this.voip.activity = false;
        this.voip.partner = false;
    }
    async onEdit() {
        await this.activityService.edit(this.props.activity.id);
    }
    async onDelete() {
        await this.activityService.delete(this.props.activity);
        await this.env.services.orm.unlink("mail.activity", [this.props.activity.id]);
        this.voip.call = false;
        this.voip.activity = false;
        this.voip.partner = false;
    }
}
Partner.props = {
    partner: {type: Object},
    activity: {type: Object, optional: true},
    call: {type: Object, optional: true},
};
Partner.template = "voip_oca.Partner";
