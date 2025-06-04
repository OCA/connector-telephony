/** @odoo-module **/
/*
    Copyright 2025 Dixmit
    License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
*/

import {Component, onWillStart, useRef, useState} from "@odoo/owl";
import {Call} from "@voip_oca/components/call/call.esm";
import {Numpad} from "@voip_oca/components/numpad/numpad.esm";
import {Partner} from "@voip_oca/components/partner/partner.esm";
import {registry} from "@web/core/registry";
import {useDebounced} from "@web/core/utils/timing";
import {useService} from "@web/core/utils/hooks";

export class VoipOCASoftphone extends Component {
    setup() {
        this.voip = useState(useService("voip_oca"));
        this.agent = useService("voip_agent_oca");
        this.searchInput = useRef("searchInput");
        this.onSearchInput = useDebounced(() => {
            this._searchInput(this.searchInput.el.value);
        }, 300);
        onWillStart(() => this._searchInput());
    }
    get showInput() {
        return Boolean(
            registry.category("voip_elements").get(this.voip.selectedTab).input
        );
    }
    get tabElements() {
        return registry
            .category("voip_elements")
            .getEntries()
            .sort((a, b) => a[1].order - b[1].order);
    }
    get childComponent() {
        const element = registry.category("voip_elements").get(this.voip.selectedTab);
        if (element) {
            return element.component;
        }
        return false;
    }
    get childComponentProps() {
        const props = {};
        const element = registry.category("voip_elements").get(this.voip.selectedTab);
        if (element.input) {
            props.records = this.voip[element.input];
        }
        return props;
    }
    async _searchInput(value) {
        const element = registry.category("voip_elements").get(this.voip.selectedTab);
        if (element && element.search) {
            await element.search(this.voip, value);
        }
    }
    /** Action */
    onClickBar() {
        this.voip.handleFold();
    }
    onCall() {
        if (this.voip.numpadTab && this.voip.numpad.value) {
            return this.agent.call({number: this.voip.numpad.value});
        }
        if (this.voip.call) {
            return this.agent.call({number: this.voip.call.phoneNumber});
        }
        if (this.voip.partner) {
            return this.agent.call({partner: this.voip.number});
        }
        const element = registry.category("voip_elements").get(this.voip.selectedTab);
        return element.call(this.voip);
    }
    onSelectTab(tag) {
        this.voip.selectedTab = tag;
        this._searchInput();
    }
    onClosePhone(ev) {
        ev.preventDefault();
        ev.stopPropagation();
        this.voip.handleVoip();
    }
    onOpenNumpad() {
        this.voip.numpadTab = !this.voip.numpadTab;
    }
}

VoipOCASoftphone.components = {Call, Numpad, Partner};
VoipOCASoftphone.props = {};
VoipOCASoftphone.template = "voip_oca.VoipOCASoftphone";

registry.category("main_components").add("voip_oca.VoipOCASoftphone", {
    Component: VoipOCASoftphone,
});
