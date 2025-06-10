/* global SIP */
/*
    Copyright 2025 Dixmit
    License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
    This service will contain all the logic necessary for the integration
    with the SIP.
*/
import {_t} from "@web/core/l10n/translation";
import {loadBundle} from "@web/core/assets";
import {reactive} from "@odoo/owl";
import {registry} from "@web/core/registry";

export class VoipAgent {
    constructor(env, services) {
        this.toneAudio = new window.Audio();
        this.callAudio = new window.Audio();
        this.voip = services.voip_oca;
        this.multiTab = services.multi_tab;
        this.orm = services.orm;
        this.notification = services.notification;
        this.session = false;
        this.isMuted = false;
        this.isHolded = false;
        this.store = services["mail.store"];
        this.connectAgent();
        return reactive(this);
    }
    get hasRtcSupport() {
        return Boolean(
            navigator.mediaDevices &&
                navigator.mediaDevices.getUserMedia &&
                window.MediaStream
        );
    }
    get agentConfig() {
        return {
            authorizationPassword: this.voip.pbx_password,
            authorizationUsername: this.voip.pbx_username,
            delegate: {
                onCallHangup: () => {
                    this.voip.inCall = false;
                },
                onInvite: this.onInvite.bind(this),
                onDisconnect: this._onDisconnect.bind(this),
            },
            logBuiltinEnabled: odoo.debug !== "",
            logLevel: odoo.debug === "" ? "error" : "debug",
            transportOptions: {
                server: this.voip.pbx_ws,
            },
            uri: SIP.UserAgent.makeURI(
                `sip:${this.voip.pbx_username}@${this.voip.pbx_domain}`
            ),
            userAgentString: `OCA SIP.js/${window.SIP.version}`,
        };
    }
    async connectAgent() {
        if (this.voip.mode !== "prod") {
            console.info("Voip agent is not available in non-production mode");
            return;
        }
        this.voip.status = "connecting";
        if (!this.hasRtcSupport) {
            console.info("Voip agent is not available in this browser");
            return;
        }
        if (!this.voip.pbx_ws || !this.voip.pbx_username || !this.voip.pbx_password) {
            console.info("Some PBX information is missing. Check your configuration");
            return;
        }
        /*
            We want to avoid errors on the navigator.
            We will only load the libraries if needed
        */
        try {
            await loadBundle("voip_oca.agent_assets");
        } catch (error) {
            console.error(error);
            this.notification.add(
                _t("Failed to load the SIP.js library:\n\n%(error)s", {
                    error: error.message,
                })
            );
            return;
        }
        try {
            this.agent = new SIP.UserAgent(this.agentConfig);
            await this.agent.start();
            this.registerer = new SIP.Registerer(this.agent);
            this.registerer.stateChange.addListener(
                this._onRegistererStateChange.bind(this)
            );
            this.registerer.register({
                requestDelegate: {
                    onReject: this._onRegistererRejected.bind(this),
                },
            });
            this.voip.status = "connected";
        } catch (error) {
            console.error(error);
            this.voip.status = "disconnected";
            this.notification.add(
                _t(
                    "An error occurred during the instantiation of the User Agent:\n\n%(error)s",
                    {
                        error: error.message,
                    }
                )
            );
            return;
        }
    }
    async reconnectAgent(attempt = 0) {
        // TODO: Show the failure in the widget somehow....
        if (attempt >= 5) {
            this.notification.add(
                _t("Failed to reconnect the User Agent. Please reload the page.")
            );
            this.voip.status = "disconnected";
            return;
        }
        if (this.reconnectingAgent) {
            return;
        }
        this.reconnectingAgent = true;
        try {
            await this.agent.reconnect();
            this.registerer.register();

            this.voip.status = "connected";
        } catch {
            // Reconnect immediately if the connection fails, then 5 seconds, then 25, 125, 625
            setTimeout(() => this.reconnectAgent(attempt + 1), 5 ** attempt * 1000);
        } finally {
            this.reconnectingAgent = false;
        }
    }
    playTone(tone) {
        this.toneAudio.currentTime = 0;
        this.toneAudio.loop = true;
        this.toneAudio.src = this.voip.tones[tone];
        this.toneAudio.play();
    }
    stopTone() {
        this.toneAudio.pause();
    }
    /* On call actions */
    async onInvite(session) {
        if (this.session) {
            // We are busy here
            session.reject({statusCode: 486});
        }
        await this.createCall({
            phone_number: session.remoteIdentity.uri.user,
            type_call: "incoming",
            state: "calling",
        });
        this.voip.inCall = true;
        this.voip.isOpened = true;
        this.voip.isFolded = false;
        session.stateChange.addListener(this._onSessionStateChange.bind(this));
        /* TODO: Modify the VOIP Widget */
        if (this.multiTab.isOnMainTab()) {
            // We will only play the calltone if we are on the main tab
            this.playTone("calltone");
            // TODO; Maybe we could send a notification???
        }
        session.delegate = {
            onBye: this._onHanghup.bind(this),
            onCancel: this._onCancelInvitation.bind(this),
        };
        this.session = session;
        this.isMuted = false;
        this.isHolded = false;
    }
    _onDisconnect(error) {
        if (!error) {
            return;
        }
        console.error(error);
        this.notification.add(
            _t("An error occurred during the connection:\n\n%(error)s", {
                error: error.message,
            })
        );

        this.voip.status = "connecting";
        this.reconnectAgent();
    }
    _onSessionStateChange(newState) {
        switch (newState) {
            case SIP.SessionState.Initial:
            case SIP.SessionState.Terminating:
            case SIP.SessionState.Establishing:
                break;
            case SIP.SessionState.Terminated:
                // We need to stop the tone if it was not established
                this.stopTone();
                break;
            case SIP.SessionState.Established:
                this.stopTone();
                this.setCallAudio();
                this.session.sessionDescriptionHandler.remoteMediaStream.onaddtrack =
                    this.setCallAudio.bind(this);
                break;
            default:
                throw new Error(`Unknown session state: "${newState}".`);
        }
    }
    setCallAudio() {
        /* We need to set the call audio of the session */
        const stream = new MediaStream();
        for (const receiver of this.session.sessionDescriptionHandler.peerConnection.getReceivers()) {
            if (receiver.track) {
                stream.addTrack(receiver.track);
            }
        }
        this.callAudio.srcObject = stream;
        this.callAudio.play();
    }
    updateCallAudio() {
        if (this.session?.sessionDescriptionHandler) {
            this.session.sessionDescriptionHandler.enableReceiverTracks(this.isHolded);
            this.session.sessionDescriptionHandler.enableSenderTracks(
                !this.isHolded && !this.isMuted
            );
        }
    }
    async createCall(options) {
        const call = await this.orm.call("voip.call", "create_call", [
            {
                pbx_id: this.voip.pbx_id,
                ...options,
            },
        ]);

        this.voip.call = this.store.Call.insert(call);
        if (call.partner) {
            this.voip.partner = this.store.Persona.insert({...call.partner});
        }
    }
    async call({number, partner}) {
        console.log(arguments);
        this.voip.isOpened = true;
        this.voip.isFolded = false;
        var phone_number = number;
        if (!number && partner) {
            phone_number = partner.mobileNumber || partner.landlineNumber;
        }
        this.playTone("dialtone");
        await this.createCall({
            partner_id: partner && partner.id,
            phone_number: phone_number,
            type_call: "outgoing",
            state: "calling",
        });
        this.voip.inCall = true;
        if (this.voip.mode === "prod") {
            const destination_number = SIP.UserAgent.makeURI(
                `sip:${phone_number.replace(/\D/g, "")}@${this.voip.pbx_domain}`
            );
            this.session = new SIP.Inviter(this.agent, destination_number);
            this.session.delegate = {
                onBye: this._onHanghup.bind(this),
            };
            this.isMuted = false;
            this.isHolded = false;
            this.session.stateChange.addListener(this._onSessionStateChange.bind(this));
            this.session
                .invite({
                    requestDelegate: {
                        onAccept: this._onInviteAccepted.bind(this),
                        onReject: this._onInviteRejected.bind(this),
                    },
                })
                .catch((error) => {
                    // This might happen, for example, if we close the call too early.
                    this.notification.add(
                        _t("Failed to establish the call:\n\n%(error)s", {
                            error: error.message,
                        })
                    );
                });
        }
    }
    transfer(number) {
        if (this.voip.mode !== "prod") {
            this._onHanghup();
            return;
        }
        this.session.refer(
            SIP.UserAgent.makeURI(`sip:${number}@${this.voip.pbx_domain}`),
            {
                requestDelegate: {
                    onAccept: this._onTransferAccepted.bind(this),
                },
            }
        );
    }
    _onTransferAccepted() {
        this.session.bye();
        this._onHanghup();
    }
    _onInviteAccepted() {
        if (!this.session) {
            return;
        }
        this.stopTone();
        this.voip.acceptCall();
    }
    _onInviteRejected(response) {
        if (!this.session) {
            return;
        }
        this.stopTone();
        this.notification.add(
            _t("Call rejected. Reason:\n\n%(reason)s", {
                reason: response.message.reasonPhrase,
            })
        );
        this.voip.rejectCall();
        this.session = null;
    }
    async _onCancelInvitation() {
        this.stopTone();
        this.voip.rejectCall();
        this.session = null;
    }
    async _onHanghup() {
        this.stopTone();
        this.callAudio.srcObject = null;
        this.callAudio.pause();
        this.voip.call.update(
            await this.orm.call("voip.call", "terminate_call", [[this.voip.call.id]])
        );
        this.voip.inCall = false;
        this.session = false;
    }
    async hangup() {
        if (this.session) {
            switch (this.session.state) {
                case SIP.SessionState.Initial:
                    if (this.voip.call.typeCall === "outgoing") {
                        this.session.cancel();
                    } else {
                        this.session.reject();
                    }
                    break;
                case SIP.SessionState.Establishing:
                    this.session.cancel();
                    break;
                case SIP.SessionState.Established:
                    this.session.bye();
                    break;
            }
        }
        this._onHanghup();
    }
    async mute() {
        this.isMuted = !this.isMuted;
        this.updateCallAudio();
    }
    async hold() {
        this.isHolded = !this.isHolded;
        try {
            await this.session.invite({
                requestDelegate: {
                    onReject() {
                        this.isHolded = !this.isHolded;
                    },
                },
                sessionDescriptionHandlerOptions: {hold: this.isHolded},
            });
        } catch (error) {
            console.error(error);
            this.notification.add(
                _t("Failed to put the call on hold/unhold:\n\n%(error)s", {
                    error: error.message.reasonPhrase,
                })
            );
        }
        this.updateCallAudio();
    }
    async accept() {
        if (this.session) {
            this.session.accept();
        }
        this.voip.acceptCall();
    }
    /* Registerer functions */
    async _onRegistererRejected(response) {
        this.notification.add(
            _t(
                "An error occurred during the registration of the User Agent:\n\n%(error)s",
                {
                    error: response.message.reasonPhrase,
                }
            )
        );
    }
    _onRegistererStateChange(state) {
        this.registererState = state;
    }
}

export const voipAgentOCAService = {
    dependencies: ["voip_oca", "multi_tab", "notification", "orm", "mail.store"],
    async start() {
        return new VoipAgent(...arguments);
    },
};

registry.category("services").add("voip_agent_oca", voipAgentOCAService);
