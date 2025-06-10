/*
    Copyright 2025 Dixmit
    License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
*/

import {Component, useState} from "@odoo/owl";
import {Numpad} from "../numpad/numpad.esm";
import {Transfer} from "../transfer/transfer.esm";
import {usePopover} from "@web/core/popover/popover_hook";
import {useService} from "@web/core/utils/hooks";

export class Call extends Component {
    setup() {
        super.setup();
        this.action = useService("action");
        this.voip = useState(useService("voip_oca"));
        this.agent = useService("voip_agent_oca");
        this.state = useState({duration: " 00:00", elapsedSeconds: 0, numpad: false});
        this.transferPopover = usePopover(Transfer, {position: "top"});
        if (this.voip.inCall) {
            this.startTimer();
        }
    }

    startTimer() {
        this.timer = setInterval(() => {
            this.state.elapsedSeconds += 1;
            const minutes = String(Math.floor(this.state.elapsedSeconds / 60)).padStart(
                2,
                "0"
            );
            const seconds = String(this.state.elapsedSeconds % 60).padStart(2, "0");
            this.state.duration = ` ${minutes}:${seconds}`;
        }, 1000);
    }

    get resId() {
        if (this.voip.activity && this.voip.activity.id) {
            return this.voip.activity.id;
        }
        return this.voip.partner.id;
    }

    get duration() {
        return this.state.duration;
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
            res_id: this.voip.partner.id,
            target: "new",
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
    onTransfer(event) {
        if (this.transferPopover.isOpen) {
            return;
        }
        this.transferPopover.open(event.currentTarget, {
            onTransfer: this.onTransferCall.bind(this),
        });
    }
    onTransferCall(transferTo) {
        if (transferTo) {
            this.agent.transfer(transferTo);
        }
    }
    onHold() {
        this.agent.hold();
    }
    onMute() {
        this.agent.mute();
    }
    onAccept() {
        this.agent.accept();
        this.state.elapsedSeconds = 0;
    }
    onHangup() {
        this.agent.hangup();
        clearInterval(this.timer);
    }
    onOpenNumpad() {
        this.state.numpad = !this.state.numpad;
    }
    onNumpadValue(key) {
        this.agent.session?.sessionDescriptionHandler.sendDtmf(key);
    }
}
Call.template = "voip_oca.Call";
Call.components = {Numpad};
