/* global SIP */
/*
    Copyright 2025 ForgeFlow, S.L.
    License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
*/
import {useState} from "@odoo/owl";
import {VoipAgent} from "@voip_oca/services/voip_agent_service.esm";
import {patch} from "@web/core/utils/patch";

let audioContext = null;
let mediaRecorder = null;
let chunks = [];

const originalOnSessionStateChange = VoipAgent.prototype._onSessionStateChange;

patch(VoipAgent.prototype, {
    setup() {
        super.setup();
        this.state = useState({call_record_mode: false});
    },
    get agentConfig() {
        const originalConfig = super.agentConfig;

        return {
            ...originalConfig,
            call_record_mode: this.voip.call_record_mode,
            call_recording_sample_rate: this.voip.call_recording_sample_rate,
        };
    },

    async startRecording() {
        if (!this.session?.sessionDescriptionHandler?.peerConnection) {
            console.warn("No active WebRTC session for recording");
            return;
        }
        const pc = this.session.sessionDescriptionHandler.peerConnection;

        // Remote + local tracks
        const remoteStream = new MediaStream();
        pc.getReceivers().forEach((receiver) => {
            if (receiver.track) {
                remoteStream.addTrack(receiver.track);
            }
        });

        try {
            mediaRecorder = new MediaRecorder(remoteStream, {mimeType: "audio/webm"});
        } catch (e) {
            console.error("MediaRecorder not supported:", e);
            return;
        }

        chunks = [];
        mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) chunks.push(event.data);
        };
        mediaRecorder.onstop = this._onRecordingStop.bind(this);

        mediaRecorder.start();
        this.voip.isRecording = true;
        console.log("Call recording started");
    },

    stopRecording() {
        if (mediaRecorder && mediaRecorder.state !== "inactive") {
            mediaRecorder.stop();
            this.voip.isRecording = false;
            console.log("Call recording stopped");
        }
    },

    async pauseRecording() {
        if (mediaRecorder && mediaRecorder.state === "recording") {
            mediaRecorder.pause();
            this.voip.isPaused = true;
        }
    },

    async resumeRecording() {
        if (mediaRecorder && mediaRecorder.state === "paused") {
            mediaRecorder.resume();
            this.voip.isPaused = false;
        }
    },

    async _blobToBase64(blob) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onloadend = () => resolve(reader.result.split(",")[1]);
            reader.onerror = reject;
            reader.readAsDataURL(blob);
        });
    },

    async _onSessionStateChange(newState) {
        await originalOnSessionStateChange.call(this, newState);
        if (newState === SIP.SessionState.Established) {
            var record_call = true;
            const record_mode = this.voip.call_record_mode || "manual";
            const sampleRate = parseFloat(this.voip.call_recording_sample_rate) || 0.0;
            if (record_mode === "sample") {
                const randomValue = Math.random() * 100;
                if (randomValue > sampleRate) {
                    record_call = false;
                }
            } else if (record_mode === "manual") {
                record_call = false;
            }
            if (record_call) {
                this.startRecording();
            }
        } else if (newState === SIP.SessionState.Terminated) {
            this.stopRecording();
        }
    },

    async _onRecordingStop() {
        // --- 5. Convert to Base64 ---
        const blob = new Blob(chunks, {type: "audio/webm"});
        const arrayBuffer = await blob.arrayBuffer();
        const base64Audio = this._arrayBufferToBase64(arrayBuffer);

        // --- 6. Upload to Odoo ---
        try {
            await this.voip.saveCallRecording(this.voip.call?.id, base64Audio);
            console.log("Recording uploaded successfully.");
        } catch (err) {
            console.error("Failed to upload recording", err);
        }

        // --- 7. Cleanup ---
        if (audioContext) {
            audioContext.close();
            audioContext = null;
        }
        mediaRecorder = null;
        chunks = [];
    },

    _arrayBufferToBase64(buffer) {
        let binary = "";
        const bytes = new Uint8Array(buffer);
        const chunkSize = 0x8000;
        for (let i = 0; i < bytes.length; i += chunkSize) {
            const chunk = bytes.subarray(i, i + chunkSize);
            binary += String.fromCharCode.apply(null, chunk);
        }
        return btoa(binary);
    },
});
