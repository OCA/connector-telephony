/*
    Copyright 2025 Dixmit
    License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
*/
import {MailActivity} from "./mock_server/mock_models/mail_activity.esm";
import {ResPartner} from "./mock_server/mock_models/res_partner.esm";
import {VoipOcaCall} from "./mock_server/mock_models/voip_call.esm";
import {VoipOcaPbx} from "./mock_server/mock_models/voip_pbx.esm";

import {defineModels} from "@web/../tests/web_test_helpers";
import {mailModels} from "@mail/../tests/mail_test_helpers";

export const voipModels = {
    MailActivity,
    ResPartner,
    VoipOcaPbx,
    VoipOcaCall,
};

export function defineVoipModels() {
    return defineModels({...mailModels, ...voipModels});
}
