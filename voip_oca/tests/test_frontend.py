# Copyright 2025 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import json
from uuid import uuid4

from odoo.tests import common


@common.tagged("post_install", "-at_install")
class TestFrontend(common.HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.pbx = cls.env["voip.pbx"].create(
            {
                "name": "Test PBX",
                "mode": "prod",
                "domain": "odoo-community.com",
                "ws_server": "wss://odoo-community.com",
            }
        )
        cls.user_password = "info"
        cls.user = common.new_test_user(
            cls.env,
            "session",
            email="session@in.fo",
            password=cls.user_password,
            tz="UTC",
        )
        cls.user.write(
            {
                "voip_pbx_id": cls.pbx.id,
                "voip_username": False,
                "voip_password": False,
            }
        )
        cls.payload = json.dumps(dict(jsonrpc="2.0", method="call", id=str(uuid4())))
        cls.headers = {
            "Content-Type": "application/json",
        }

    def test_session_unconfigured(self):
        self.authenticate(self.user.login, self.user_password)
        response = self.url_open(
            "/web/session/get_session_info", data=self.payload, headers=self.headers
        )
        self.assertEqual(response.status_code, 200)
        session_info = response.json()["result"]
        self.assertEqual(session_info["voip"]["pbx_id"], self.pbx.id)
        self.assertEqual(session_info["voip"]["mode"], "test")

    def test_session_configured(self):
        self.user.write(
            {
                "voip_username": "test",
                "voip_password": "test",
            }
        )
        self.authenticate(self.user.login, self.user_password)
        response = self.url_open(
            "/web/session/get_session_info", data=self.payload, headers=self.headers
        )
        self.assertEqual(response.status_code, 200)
        session_info = response.json()["result"]
        self.assertEqual(session_info["voip"]["pbx_id"], self.pbx.id)
        self.assertEqual(session_info["voip"]["mode"], "prod")

    def test_javascript(self):
        self.browser_js("/web/tests?module=voip_oca", "", login="admin", timeout=1800)
