# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

import logging

from odoo import fields, models
from odoo.tools import groupby

_logger = logging.getLogger(__name__)


class SmsSms(models.Model):
    _inherit = "sms.sms"

    sms_gateway_id = fields.Many2one("ir.sms.gateway", string="SMS gateway used")

    def _split_by_api(self):
        """Override to split by SMS gateway instead of just API."""
        # First, assign gateways to SMS records that don't have one
        self._assign_gateways()

        # Group by gateway
        for gateway_id, gateway_sms in groupby(
            self, key=lambda sms: sms.sms_gateway_id
        ):
            gateway_sms_list = list(gateway_sms)

            if gateway_id and gateway_id.gateway_type != "iap":
                # For custom gateways, use Custom as API - they'll be handled in _send
                yield "Custom", self.env["sms.sms"].concat(*gateway_sms_list)
            else:
                # For IAP, use standard behavior
                company = self._get_sms_company()
                yield (
                    company._get_sms_api_class()(self.env),
                    self.env["sms.sms"].concat(*gateway_sms_list),
                )

    def _assign_gateways(self):
        """Assign appropriate gateways to SMS records that don't have one."""
        sms_without_gateway = self.filtered(lambda s: not s.sms_gateway_id)
        _logger.info("Found %s SMS records without gateway", len(sms_without_gateway))

        if not sms_without_gateway:
            return

        # Get available gateways
        IrSmsGateway = self.env["ir.sms.gateway"]
        providers = IrSmsGateway._send_get_providers([])
        _logger.info("Available providers: %s", providers.mapped("name"))

        for sms in sms_without_gateway:
            # Find the best gateway for this SMS
            matching_providers = []
            for provider in providers:
                if provider._can_send({"number": sms.number}):
                    matching_providers.append(provider)
                    _logger.info(
                        "Provider %s can send to %s", provider.name, sms.number
                    )

            if matching_providers:
                # Sort by sequence (lower sequence = higher priority)
                best_gateway = min(matching_providers, key=lambda p: p.sequence)
                sms.sms_gateway_id = best_gateway
                _logger.info("Assigned gateway %s to SMS %s", best_gateway.name, sms.id)
            else:
                # If no specific gateway matches, use gateways
                # with no prefix restrictions as fallback
                fallback_providers = providers.filtered(lambda p: not p.prefix)
                if fallback_providers:
                    # Use the fallback gateway with lowest sequence
                    fallback_gateway = min(fallback_providers, key=lambda p: p.sequence)
                    sms.sms_gateway_id = fallback_gateway
                else:
                    # If no fallback either, use the first
                    # available gateway as last resort
                    if providers:
                        last_resort_gateway = min(providers, key=lambda p: p.sequence)
                        sms.sms_gateway_id = last_resort_gateway
                    else:
                        _logger.error("No gateways available for SMS %s", sms.id)

    def _send_with_api(
        self, sms_api, unlink_failed=False, unlink_sent=True, raise_exception=False
    ):
        """Override to handle custom SMS gateways."""
        _logger.info("_send_with_api called with api: %s, SMS: %s", sms_api, self.ids)

        # If no API provided (custom gateway), use custom gateway handling
        if sms_api == "Custom":
            return self._send_with_custom_gateway(
                unlink_failed, unlink_sent, raise_exception
            )

        # Otherwise, use standard IAP handling
        return super()._send_with_api(
            sms_api,
            unlink_failed=unlink_failed,
            unlink_sent=unlink_sent,
            raise_exception=raise_exception,
        )

    def _send_with_custom_gateway(
        self, unlink_failed=False, unlink_sent=True, raise_exception=False
    ):
        """Handle sending with custom SMS gateway."""
        _logger.info("_send_with_custom_gateway called for SMS: %s", self.ids)
        IrSmsGateway = self.env["ir.sms.gateway"]

        # Group SMS by gateway
        gateway_groups = {}
        for sms in self:
            gateway_id = sms.sms_gateway_id.id
            gateway_groups.setdefault(gateway_id, []).append(sms.id)

        all_results = []

        for gateway_id, sms_ids in gateway_groups.items():
            if not gateway_id:
                continue

            gateway = IrSmsGateway.browse(gateway_id)
            # Ensure sms_records is a proper recordset
            sms_records = self.env["sms.sms"].browse(sms_ids)
            _logger.info(
                "Processing %s SMS with gateway %s", len(sms_records), gateway.name
            )

            if gateway.gateway_type == "iap":
                # Use standard IAP for IAP-type gateways
                company = sms_records._get_sms_company()
                sms_api = company._get_sms_api_class()(self.env)
                sms_records._send_with_api(
                    sms_api,
                    unlink_failed=unlink_failed,
                    unlink_sent=unlink_sent,
                    raise_exception=raise_exception,
                )
            else:
                # Use custom gateway - prepare messages in the expected format
                messages = []
                for sms in sms_records:
                    messages.append(
                        {
                            "id": sms.id,
                            "uuid": sms.uuid,
                            "number": sms.number,
                            "content": sms.body,
                        }
                    )

                # Call the gateway's send method
                try:
                    results = gateway._send_sms_batch(messages)
                    _logger.info("Custom gateway %s results: %s", gateway.name, results)
                except Exception as e:
                    _logger.error("Custom gateway %s failed: %s", gateway.name, e)
                    if raise_exception:
                        raise
                    # Create error results for all messages
                    results = [
                        {
                            "uuid": sms.uuid,
                            "state": "server_error",
                            "failure_reason": str(e),
                        }
                        for sms in sms_records
                    ]

                # Process the results to update SMS records
                sms_records._process_custom_gateway_results(
                    results, unlink_failed=unlink_failed, unlink_sent=unlink_sent
                )
                all_results.extend(results)

        return all_results

    def _process_custom_gateway_results(
        self, results, unlink_failed=False, unlink_sent=True
    ):
        """Process results from custom gateway and update SMS records."""
        if not results:
            return

        results_uuids = [result["uuid"] for result in results]
        all_sms_sudo = (
            self.env["sms.sms"]
            .sudo()
            .search([("uuid", "in", results_uuids)])
            .with_context(sms_skip_msg_notification=True)
        )

        # Define state mappings for custom gateways - matching Odoo's pattern
        IAP_TO_SMS_STATE_SUCCESS = {
            "success": "sent",
            "accepted": "sent",
            "sent": "sent",
            "delivered": "sent",
        }

        # Map IAP states to SMS failure types
        PROVIDER_TO_SMS_FAILURE_TYPE = {
            "server_error": "sms_server",
            "invalid_number": "sms_number_format",
            "insufficient_credit": "sms_credit",
            "unauthorized": "sms_acc",
            "wrong_api_key": "sms_acc",
            "network_error": "sms_server",
            "timeout": "sms_server",
        }

        # Group results by state and failure_reason
        for (iap_state, failure_reason), results_group in groupby(
            sorted(
                results, key=lambda x: (x.get("state"), x.get("failure_reason", ""))
            ),
            key=lambda result: (
                result.get("state"),
                result.get("failure_reason", False),
            ),
        ):
            results_group_list = list(results_group)

            # Create a set of UUIDs for this group
            group_uuids = {result["uuid"] for result in results_group_list}

            def _filter_by_uuids(records, uuids_set):
                return records.filtered(lambda r: r.uuid in uuids_set)

            sms_sudo = _filter_by_uuids(all_sms_sudo, group_uuids)

            if not sms_sudo:
                continue

            if success_state := IAP_TO_SMS_STATE_SUCCESS.get(iap_state):
                # Success case - mark as sent
                sms_sudo.sms_tracker_id._action_update_from_sms_state(success_state)
                to_delete = {"to_delete": True} if unlink_sent else {}
                sms_sudo.write(
                    {
                        "state": success_state,
                        "failure_type": False,  # Clear failure type for success
                        **to_delete,
                    }
                )
                _logger.info("Marked %s SMS as sent: %s", len(sms_sudo), sms_sudo.ids)
            else:
                # Error case - determine failure_type from iap_state
                failure_type = PROVIDER_TO_SMS_FAILURE_TYPE.get(iap_state, "unknown")

                # Update SMS tracker with both failure_type and failure_reason
                if failure_type != "unknown":
                    sms_sudo.sms_tracker_id._action_update_from_sms_state(
                        "error",
                        failure_type=failure_type,
                        failure_reason=failure_reason,
                    )
                else:
                    sms_sudo.sms_tracker_id.with_context(
                        sms_known_failure_reason=failure_reason
                    )._action_update_from_provider_error(iap_state)

                # Update SMS record - only set state and failure_type
                # (no failure_reason field)
                to_delete = {"to_delete": True} if unlink_failed else {}
                sms_sudo.write(
                    {
                        "state": "error",
                        "failure_type": failure_type,  # Set the failure_type only
                        **to_delete,
                    }
                )
                _logger.warning(
                    "Marked %s SMS as error (type: %s, reason: %s): %s",
                    len(sms_sudo),
                    failure_type,
                    failure_reason,
                    sms_sudo.ids,
                )

        # Call hooks and notifications
        all_sms_sudo._handle_call_result_hook(results)
        all_sms_sudo.mail_message_id._notify_message_notification_update()
