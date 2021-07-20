# Copyright (C) 2019 Open Source Integrators
# <https://www.opensourceintegrators.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestBackendVoicent(TransactionCase):
    def setUp(self):
        super(TestBackendVoicent, self).setUp()
        self.backend_voicent_model = self.env["backend.voicent"]
        self.backend_voicent_id = self.backend_voicent_model.create(
            {
                "name": "Test",
                "host": "localhost",
                "port": "8155",
                "callerid": "0000000000",
                "line": "1",
                "active": True,
                "call_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "call 1",
                            "applies_on": False,
                            "msgtype": "tts",
                            "msginfo": "Hello World!",
                        },
                    )
                ],
                "time_line_ids": [
                    (0, 0, {"name": "Call Time 1", "time": 10.0}),
                    (0, 0, {"name": "Call Time 2", "time": 11.0}),
                    (0, 0, {"name": "Call Time 3", "time": 12.0}),
                    (0, 0, {"name": "Call Time 4", "time": 13.0}),
                ],
            }
        )

    def test_run_check_the_voicent_status(self):
        """To call the scheduler method."""
        self.backend_voicent_id._run_update_next_call()
