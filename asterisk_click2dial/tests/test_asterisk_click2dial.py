# Copyright 2026 Christos <ioannidisc@kekmentor.gr>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from unittest.mock import Mock, patch

import requests

from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import TransactionCase, tagged
from odoo.tools import mute_logger

MOCK_GET = "odoo.addons.asterisk_click2dial.models.asterisk_server.requests.get"
MOCK_POST = "odoo.addons.asterisk_click2dial.models.phone_common.requests.post"
IMPOSSIBLE_NUMBER = "99999999999999999999"


@tagged("post_install", "-at_install")
class TestAsteriskClick2dial(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if not cls.env.company.country_id:
            cls.env.company.country_id = cls.env.ref("base.fr")
        cls.server = cls.env["asterisk.server"].create(
            {
                "name": "Test Asterisk",
                "ip_address": "asterisk.example.com",
                "login": "ari_login",
                "password": "ari_pass",
                "context": "from-internal",
                "out_prefix": "0",
                "company_id": cls.env.company.id,
            }
        )
        cls.user = (
            cls.env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "Click2dial User",
                    "login": "test_click2dial_user",
                    "company_id": cls.env.company.id,
                    "company_ids": [(6, 0, [cls.env.company.id])],
                    "internal_number": "101",
                    "callerid": "Click2dial User <101>",
                    "asterisk_chan_type": "PJSIP",
                    "resource": "phone-test",
                    "asterisk_server_id": cls.server.id,
                }
            )
        )

    def _require_resource(self):
        # another installed module may turn 'resource' into a related
        # readonly field (e.g. hotdesking setups)
        if not self.user.resource:
            self.skipTest("resource field is driven by another installed module")

    def test_server_out_prefix_digits_only(self):
        with self.assertRaises(ValidationError):
            self.server.write({"out_prefix": "abc"})

    def test_server_wait_time_range(self):
        with self.assertRaises(ValidationError):
            self.server.write({"wait_time": 0})
        with self.assertRaises(ValidationError):
            self.server.write({"wait_time": 121})

    def test_server_extension_priority_positive(self):
        with self.assertRaises(ValidationError):
            self.server.write({"extension_priority": 0})

    def test_server_port_range(self):
        with self.assertRaises(ValidationError):
            self.server.write({"port": 0})
        with self.assertRaises(ValidationError):
            self.server.write({"port": 65536})

    def test_server_ascii_fields(self):
        for field in ("context", "alert_info", "login", "password"):
            with self.assertRaises(ValidationError):
                self.server.write({field: "μη-ascii"})

    def test_user_ascii_fields(self):
        for field in ("resource", "internal_number", "callerid"):
            with self.assertRaises(ValidationError):
                self.user.write({field: "μη-ascii"})

    def test_asterisk_chan_name_compute(self):
        self._require_resource()
        self.assertEqual(self.user.asterisk_chan_name, "PJSIP/phone-test")
        self.user.write({"resource": False})
        self.assertFalse(self.user.asterisk_chan_name)

    def test_get_asterisk_server_from_user(self):
        self.assertEqual(self.user.get_asterisk_server_from_user(), self.server)
        other_servers = self.env["asterisk.server"].search(
            [("id", "!=", self.server.id)]
        )
        other_servers.write({"active": False})
        self.user.write({"asterisk_server_id": False})
        self.assertEqual(self.user.get_asterisk_server_from_user(), self.server)
        self.server.write({"active": False})
        with self.assertRaises(UserError):
            self.user.get_asterisk_server_from_user()

    @patch(MOCK_GET)
    def test_ari_connection_ok(self, mock_get):
        mock_get.return_value = Mock(status_code=200)
        action = self.server.test_ari_connection()
        self.assertEqual(action["tag"], "display_notification")
        self.assertEqual(action["params"]["type"], "success")

    @patch(MOCK_GET)
    def test_ari_connection_http_error(self, mock_get):
        mock_get.return_value = Mock(status_code=401)
        with self.assertRaises(UserError):
            self.server.test_ari_connection()

    @patch(MOCK_GET)
    def test_ari_connection_unreachable(self, mock_get):
        mock_get.side_effect = requests.exceptions.ConnectionError("unreachable")
        with self.assertRaises(UserError):
            self.server.test_ari_connection()

    def _channel(self, state="Up", name="PJSIP/phone-test-00000001"):
        return {
            "state": state,
            "name": name,
            "connected": {"number": IMPOSSIBLE_NUMBER},
        }

    def test_get_calling_number_from_channel(self):
        self._require_resource()
        aso = self.env["asterisk.server"]
        self.assertEqual(
            aso._get_calling_number_from_channel(self._channel(), self.user),
            IMPOSSIBLE_NUMBER,
        )
        self.assertFalse(
            aso._get_calling_number_from_channel(self._channel(state="Down"), self.user)
        )
        self.assertFalse(
            aso._get_calling_number_from_channel(
                self._channel(name="PJSIP/other-00000001"), self.user
            )
        )

    @patch(MOCK_GET)
    def test_get_record_from_my_channel(self, mock_get):
        self._require_resource()
        mock_get.return_value = Mock(status_code=200)
        mock_get.return_value.json.return_value = [self._channel()]
        aso = self.env["asterisk.server"].with_user(self.user)
        self.assertEqual(aso.get_record_from_my_channel(), IMPOSSIBLE_NUMBER)

    @patch(MOCK_GET)
    @mute_logger("odoo.addons.asterisk_click2dial.models.asterisk_server")
    def test_get_calling_number_http_error(self, mock_get):
        mock_get.return_value = Mock(status_code=500)
        aso = self.env["asterisk.server"].with_user(self.user)
        self.assertFalse(aso.get_record_from_my_channel())

    @patch(MOCK_GET)
    @mute_logger("odoo.addons.asterisk_click2dial.models.asterisk_server")
    def test_get_calling_number_unreachable(self, mock_get):
        mock_get.side_effect = requests.exceptions.ConnectionError("unreachable")
        aso = self.env["asterisk.server"].with_user(self.user)
        with self.assertRaises(UserError):
            aso.get_record_from_my_channel()

    @patch(MOCK_POST)
    def test_click2dial(self, mock_post):
        self._require_resource()
        mock_post.return_value = Mock(status_code=200)
        pc = self.env["phone.common"].with_user(self.user)
        erp_number = "+33 1 41 98 12 42"
        res = pc.click2dial(erp_number)
        expected = "0" + pc.convert_to_dial_number(erp_number)
        self.assertEqual(res["dialed_number"], expected)
        params = mock_post.call_args.kwargs["params"]
        self.assertEqual(params["endpoint"], "PJSIP/phone-test")
        self.assertEqual(params["extension"], expected)
        self.assertEqual(params["context"], "from-internal")
        self.assertEqual(params["callerId"], self.user.callerid)

    @patch(MOCK_POST)
    def test_click2dial_options(self, mock_post):
        self._require_resource()
        mock_post.return_value = Mock(status_code=200)
        self.user.write(
            {"dial_suffix": "aa=2wb", "alert_info": "ring1", "variable": "X=1|Y=2"}
        )
        pc = self.env["phone.common"].with_user(self.user)
        pc.click2dial("+33 1 41 98 12 42")
        params = mock_post.call_args.kwargs["params"]
        self.assertEqual(params["endpoint"], "PJSIP/phone-test/aa=2wb")
        self.user.write({"alert_info": False})
        self.server.write({"alert_info": "ring2"})
        pc.click2dial("+33 1 41 98 12 42")

    def test_click2dial_missing_number(self):
        pc = self.env["phone.common"].with_user(self.user)
        with self.assertRaises(UserError):
            pc.click2dial(False)

    @patch(MOCK_POST)
    def test_click2dial_no_callerid(self, mock_post):
        mock_post.return_value = Mock(status_code=200)
        self.user.write({"callerid": False})
        pc = self.env["phone.common"].with_user(self.user)
        with self.assertRaises(UserError):
            pc.click2dial("+33 1 41 98 12 42")

    @patch(MOCK_POST)
    def test_click2dial_http_error(self, mock_post):
        mock_post.return_value = Mock(status_code=500)
        pc = self.env["phone.common"].with_user(self.user)
        with self.assertRaises(UserError):
            pc.click2dial("+33 1 41 98 12 42")

    @patch(MOCK_POST)
    @mute_logger("odoo.addons.asterisk_click2dial.models.phone_common")
    def test_click2dial_unreachable(self, mock_post):
        mock_post.side_effect = requests.exceptions.ConnectionError("unreachable")
        pc = self.env["phone.common"].with_user(self.user)
        with self.assertRaises(UserError):
            pc.click2dial("+33 1 41 98 12 42")
