# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

from odoo.tests.common import TransactionCase


class TestSmsAlternativeProvider(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.iap_gateway = cls.env.ref("sms_alternative_provider.gateway_iap")
        # Ensure the IAP gateway is active and has no prefix restrictions
        cls.iap_gateway.write(
            {
                "active": True,
                "prefix": False,
                "sequence": 10,
            }
        )

    def test_gateway_assignment_priority(self):
        """Test that gateway assignment respects sequence priority"""
        # Create multiple gateways that can handle the same number
        gw_high_priority = self.env["ir.sms.gateway"].create(
            {
                "name": "High Priority Gateway",
                "gateway_type": "iap",
                "prefix": False,
                "sequence": 1,
                "active": True,
            }
        )
        sms = self.env["sms.sms"].create(
            {
                "number": "+123456789",
                "body": "test message",
            }
        )

        # Test gateway assignment
        sms._assign_gateways()

        # Should use the highest priority (lowest sequence) gateway
        self.assertEqual(
            sms.sms_gateway_id,
            gw_high_priority,
            "Should assign gateway with lowest sequence number",
        )

    def test_prefix_restrictions(self):
        """Test that prefix restrictions work correctly in gateway assignment"""
        gw_us_only = self.env["ir.sms.gateway"].create(
            {
                "name": "US Only Gateway",
                "gateway_type": "iap",
                "prefix": "+1",
                "sequence": 1,
                "active": True,
            }
        )
        gw_eu_only = self.env["ir.sms.gateway"].create(
            {
                "name": "EU Only Gateway",
                "gateway_type": "iap",
                "prefix": "+49 +33",
                "sequence": 1,
                "active": True,
            }
        )

        # Test US number should be assigned to US gateway
        sms_us = self.env["sms.sms"].create(
            {
                "number": "+1 5551234",
                "body": "US message",
            }
        )
        sms_us._assign_gateways()
        self.assertEqual(
            sms_us.sms_gateway_id,
            gw_us_only,
            "US number should be assigned to US gateway",
        )

        # Test German number should be assigned to EU gateway
        sms_de = self.env["sms.sms"].create(
            {
                "number": "+49 30123456",
                "body": "German message",
            }
        )
        sms_de._assign_gateways()
        self.assertEqual(
            sms_de.sms_gateway_id,
            gw_eu_only,
            "German number should be assigned to EU gateway",
        )

    def test_provider_partitioning(self):
        """Test that provider partitioning works correctly"""
        gw_priority_1 = self.env["ir.sms.gateway"].create(
            {
                "name": "Priority 1 Gateway",
                "gateway_type": "iap",
                "prefix": False,
                "sequence": 1,
                "active": True,
            }
        )
        gw_priority_2 = self.env["ir.sms.gateway"].create(
            {
                "name": "Priority 2 Gateway",
                "gateway_type": "iap",
                "prefix": False,
                "sequence": 2,
                "active": True,
            }
        )

        # Test messages partitioning
        messages = [
            {"id": 1, "number": "+123456789", "content": "test message 1"},
            {"id": 2, "number": "+987654321", "content": "test message 2"},
        ]

        providers = self.env["ir.sms.gateway"]._send_get_providers(messages)
        provider2messages = providers._send_partition_providers(messages)

        # Should assign all messages to the highest priority provider
        self.assertIn(gw_priority_1, provider2messages)
        self.assertEqual(len(provider2messages[gw_priority_1]), 2)
        self.assertNotIn(gw_priority_2, provider2messages)

    def test_can_send_logic(self):
        """Test the _can_send method with various prefix configurations"""
        gateway = self.env["ir.sms.gateway"].create(
            {
                "name": "Test Gateway",
                "gateway_type": "iap",
                "prefix": "+1 +44",
                "sequence": 1,
                "active": True,
            }
        )

        # Test numbers that should match
        self.assertTrue(
            gateway._can_send({"number": "+1 5551234"}), "Should match +1 prefix"
        )
        self.assertTrue(
            gateway._can_send({"number": "+44 2071234567"}), "Should match +44 prefix"
        )

        # Test numbers that should not match
        self.assertFalse(
            gateway._can_send({"number": "+33 123456789"}),
            "Should not match +33 prefix",
        )
        self.assertFalse(
            gateway._can_send({"number": "123456789"}),
            "Should not match number without prefix",
        )

    def test_gateway_with_no_prefix(self):
        """Test gateway with no prefix restrictions"""
        gateway_no_prefix = self.env["ir.sms.gateway"].create(
            {
                "name": "No Prefix Gateway",
                "gateway_type": "iap",
                "prefix": False,  # No restrictions
                "sequence": 1,
                "active": True,
            }
        )

        # Should be able to send to any number
        self.assertTrue(
            gateway_no_prefix._can_send({"number": "+1 5551234"}),
            "Should send to US number",
        )
        self.assertTrue(
            gateway_no_prefix._can_send({"number": "+44 2071234567"}),
            "Should send to UK number",
        )
        self.assertTrue(
            gateway_no_prefix._can_send({"number": "123456789"}),
            "Should send to number without country code",
        )
