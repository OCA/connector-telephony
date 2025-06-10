/*
    Copyright 2025 Dixmit
    License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
*/
import {fields, models} from "@web/../tests/web_test_helpers";

export class VoipOcaPbx extends models.ServerModel {
    _name = "voip.pbx";

    name = fields.Char();
    domain = fields.Char();
    ws_server = fields.Char();
    mode = fields.Selection({
        selection: [
            ["test", "Test"],
            ["production", "Production"],
        ],
        default: "test",
    });

    _records = [
        {
            id: 1,
            name: "Test PBX",
            domain: "pbx.domain",
            ws_server: "wss://pbx.domain",
            mode: "test",
        },
    ];
}
