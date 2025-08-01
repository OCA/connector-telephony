/*
    Copyright 2025 ForgeFlow, S.L.
    License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
*/
import {useState} from "@odoo/owl";
import {VoipOCA} from "@voip_oca/services/voip_oca_service.esm";
import {patch} from "@web/core/utils/patch";

patch(VoipOCA.prototype, {
    /**
     * Upload call recording to Odoo
     * @param {Number} callId
     * @param {String} base64Audio - with or without data: prefix
     * @param {String} filename
     */
    setup() {
        super.setup();
        this.state = useState({isRecording: false, isPaused: false});
    },
    async saveCallRecording(callId, base64Audio) {
        if (!callId) {
            throw new Error("Invalid call id for recording upload");
        }
        const audioData = base64Audio.startsWith("data:")
            ? base64Audio
            : `data:audio/webm;base64,${base64Audio}`;
        return this.orm.call("voip.call", "save_call_recording", [callId, audioData]);
    },
});
