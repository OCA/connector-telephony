/*
    Copyright 2025 Dixmit
    License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
    This service will contain all the items necessary for the views
    of the voip widgets.
*/
import {matchString} from "../utils/utils.esm";
import {reactive} from "@odoo/owl";
import {registry} from "@web/core/registry";
import {session} from "@web/session";
import {url} from "@web/core/utils/urls";
import {user} from "@web/core/user";

export class VoipOCA {
    constructor(env, services) {
        /* Store voip data in the service, not the session */
        Object.assign(this, session.voip);
        delete session.voip;
        this.status = "disconnected";
        this.selectedTab = "activity_list";
        this.uid = user.userId;
        this.store = services["mail.store"];
        this.numpadTab = false;
        this.orm = services.orm;
        this.isOpened = false;
        this.isFolded = false;
        this.partner = false;
        this.activity = false;
        this.call = false;
        this.inCall = false;
        this.searchValue = "";
        this.numpad = {
            isOpen: false,
            value: "",
            selection: {
                start: 0,
                end: 0,
                direction: "none",
            },
        };
        this.user = env.services.user;
        // We will make this service reactive,
        // this way we will hanble the changes on the component
        return reactive(this);
    }
    /* Widget Buttons */
    handleVoip() {
        if (!this.isOpened) {
            this.isFolded = false;
        }
        this.isOpened = !this.isOpened;
    }
    handleFold() {
        this.isFolded = !this.isFolded;
    }
    async open({partner = false, activity = false, call = false}) {
        let partner_id = partner && partner.id;
        if (activity) {
            partner_id = activity.main_partner_id && activity.main_partner_id[0];
        } else if (call) {
            partner_id = call.partner && call.partner.id;
        }
        this.activity = activity || {};
        this.call = call || {};
        this.partner = await this.orm.call("res.partner", "format_partner", [
            [partner_id],
        ]);
    }
    async acceptCall() {
        this.call.update(
            await this.orm.call("voip.call", "accept_call", [[this.call.id]])
        );
    }
    async rejectCall() {
        this.call.update(
            await this.orm.call("voip.call", "reject_call", [[this.call.id]])
        );
        this.inCall = false;
        this.call = false;
    }
    /* Elements */

    get partners() {
        return Object.values(this.store.Persona.records).filter(
            (partner) =>
                partner.hasPhoneNumber &&
                (!this.searchValue ||
                    [
                        partner.name,
                        partner.displayName,
                        partner.mobileNumber,
                        partner.landlineNumber,
                    ].some((x) => matchString(x, this.searchValue)))
        );
    }
    get activities() {
        return Object.values(this.store.Activity.records).filter(
            (activity) =>
                (!this.searchValue ||
                    [activity.summary, activity.resName, activity.main_partner].some(
                        (x) => matchString(x, this.searchValue)
                    )) &&
                new Date(activity.date_deadline) <= new Date() &&
                activity.activity_category === "phonecall" &&
                activity.user_id[0] === this.uid
        );
    }

    get calls() {
        return Object.values(this.store.Call.records)
            .filter(
                (call) =>
                    !this.searchValue ||
                    [call.phoneNumber, call.displayName].some((x) =>
                        matchString(x, this.searchValue)
                    )
            )
            .sort((a, b) => b.date - a.date);
    }
    get partnerProps() {
        return {
            partner: this.partner || {},
            activity: this.activity || {},
            call: this.call || {},
        };
    }

    /* Search functions */
    async searchPartners(_search = "", offset = 0, limit = 13) {
        const partners = await this.orm.call("res.partner", "voip_get_contacts", [], {
            offset,
            limit,
            _search,
        });
        for (const partner of partners) {
            this.store.Persona.insert({...partner, type: "partner"});
        }
    }
    async searchActivities(_search = "", offset = 0, limit = 13) {
        const activities = await this.orm.call(
            "mail.activity",
            "get_call_activities",
            [],
            {
                offset,
                limit,
                _search,
            }
        );
        if (!activities["mail.activity"]) {
            return;
        }
        for (const activity of activities["mail.activity"]) {
            this.store.Activity.insert({...activity});
        }
    }
    async searchCalls(_search = "", offset = 0, limit = 13) {
        const calls = await this.orm.call("voip.call", "get_recent_calls", [], {
            offset,
            limit,
            _search,
        });
        for (const call of calls) {
            this.store.Call.insert({...call});
        }
    }
    /* Image functions */
    imagePartner(partner_id) {
        return url("/web/image", {
            model: "res.partner",
            id: partner_id,
            field: "avatar_128",
        });
    }
}

export const voipOCAService = {
    dependencies: ["mail.store", "orm"],
    async start() {
        return new VoipOCA(...arguments);
    },
};

registry.category("services").add("voip_oca", voipOCAService);
