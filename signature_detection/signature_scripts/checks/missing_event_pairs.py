from __future__ import annotations

from db.repository.detection_alert.detection_alert_model import DetectionAlert
from signature_detection.constants import (
    BRIDGE_CCTX_TIMEOUTS,
    AlertSeverity,
    EventPairFlow,
    SignatureType,
)


class MissingEventPairsMixin:
    def _unique_transaction_events(self, events: list) -> list:
        unique_events = []
        seen_transactions = set()

        for event in events:
            transaction_hash = getattr(event, "transaction_hash", None)
            transaction_key = (
                str(transaction_hash).lower()
                if transaction_hash is not None
                else f"event:{getattr(event, 'id', len(unique_events))}"
            )
            if transaction_key in seen_transactions:
                continue
            seen_transactions.add(transaction_key)
            unique_events.append(event)

        return unique_events

    def _cctx_correlation_id(self, bridge: str, cctx) -> str:
        cctx_id = getattr(cctx, "cctx_id", None)
        if cctx_id is not None:
            return str(cctx_id)

        for field in ("deposit_id", "id"):
            value = getattr(cctx, field, None)
            if value is not None:
                return f"{bridge}:{field}:{value}"

        return f"{bridge}:unknown_cctx"

    def _side_has_transaction(self, cctx, side: str) -> bool:
        return getattr(cctx, f"{side}_transaction_hash", None) is not None

    def _cctx_side_timestamp(self, cctx, side: str) -> int | None:
        return getattr(cctx, f"{side}_timestamp", None)

    def _cctx_side_blockchain(self, cctx, side: str) -> str | None:
        return getattr(cctx, f"{side}_blockchain", None)

    def incomplete_cross_chain_transactions(
        self,
        bridge: str,
        cctxs: list | None = None,
    ) -> list[DetectionAlert]:
        """
        Alert when a cross-chain transaction row has only one side populated.

        This is useful for manually curated datasets that have transaction/CCTX
        rows but no normalized events yet. A dst-only row is treated as a
        mint/release without a source lock; a src-only row is treated as a lock
        without a destination mint/release.
        """
        print("starting analysis for incomplete_cross_chain_transactions")
        alerts = []

        if cctxs is None:
            cctxs = self._analysis_cross_chain_transactions()

        for cctx in cctxs:
            has_source = self._side_has_transaction(cctx, "src")
            has_destination = self._side_has_transaction(cctx, "dst")
            if has_source == has_destination:
                continue

            cctx_id = self._cctx_correlation_id(bridge, cctx)
            if has_destination:
                timestamp = self._cctx_side_timestamp(cctx, "dst")
                if not self._is_timestamp_in_analysis_window(timestamp):
                    continue
                transaction_hash = getattr(cctx, "dst_transaction_hash", None)
                severity = AlertSeverity.HIGH
                description_suffix = "Destination transaction exists, but no source transaction is present in the CCTX row."
                if self._event_is_recent(
                    bridge,
                    timestamp,
                    None,
                    self._cctx_side_blockchain(cctx, "dst"),
                ):
                    severity = AlertSeverity.MEDIUM
                    description_suffix = "Destination transaction exists without a source transaction, but it is still within the expected processing window."
                alerts.append(
                    self.create_detection_alert(
                        signature_type=SignatureType.MINT_WITHOUT_LOCK,
                        severity=severity,
                        bridge=bridge,
                        correlation_id=cctx_id,
                        correlation_type="dst_only_cross_chain_transaction",
                        src_event_id=None,
                        dst_event_id=None,
                        title=f"{bridge}: destination transaction without source transaction",
                        description=(
                            f"Found CCTX {cctx_id} with dst_transaction_hash={transaction_hash}. "
                            f"{description_suffix}"
                        ),
                        created_at_ts=timestamp,
                        probability=self._missing_pair_attack_probability(
                            bridge,
                            timestamp,
                            missing_side="source",
                        ),
                    )
                )
                continue

            timestamp = self._cctx_side_timestamp(cctx, "src")
            if not self._is_timestamp_in_analysis_window(timestamp):
                continue
            transaction_hash = getattr(cctx, "src_transaction_hash", None)
            severity = AlertSeverity.MEDIUM
            description_suffix = "Source transaction exists, but no destination transaction is present in the CCTX row."
            if self._event_is_recent(
                bridge,
                timestamp,
                None,
                self._cctx_side_blockchain(cctx, "src"),
            ):
                severity = AlertSeverity.LOW
                description_suffix = "Source transaction exists without a destination transaction, but it is still within the expected processing window."
            alerts.append(
                self.create_detection_alert(
                    signature_type=SignatureType.LOCK_WITHOUT_MINT,
                    severity=severity,
                    bridge=bridge,
                    correlation_id=cctx_id,
                    correlation_type="src_only_cross_chain_transaction",
                    src_event_id=None,
                    dst_event_id=None,
                    title=f"{bridge}: source transaction without destination transaction",
                    description=(
                        f"Found CCTX {cctx_id} with src_transaction_hash={transaction_hash}. "
                        f"{description_suffix}"
                    ),
                    created_at_ts=timestamp,
                    probability=self._missing_pair_attack_probability(
                        bridge,
                        timestamp,
                        missing_side="destination",
                    ),
                )
            )

        print(f"cought {len(alerts)} alerts")
        return alerts

    def _missing_pair_attack_probability(
        self,
        bridge: str,
        event_timestamp: int | None,
        missing_side: str | None = None,
    ) -> str:
        if event_timestamp is None:
            return "UNKNOWN: event timestamp is unavailable."

        start_ts = getattr(self, "_analysis_start_ts", None)
        end_ts = getattr(self, "_analysis_end_ts", None)
        boundary = None
        boundary_name = None
        if missing_side == "destination":
            boundary = end_ts
            boundary_name = "end"
        elif missing_side == "source":
            boundary = start_ts
            boundary_name = "start"

        if boundary is None:
            window_boundaries = [
                candidate for candidate in (start_ts, end_ts) if candidate is not None
            ]
            if window_boundaries:
                boundary = min(
                    window_boundaries,
                    key=lambda candidate: abs(event_timestamp - candidate),
                )
                boundary_name = "closest"

        if boundary is None:
            return "HIGH: no analysis time window was configured."

        bridge_timeout = BRIDGE_CCTX_TIMEOUTS.get(bridge)
        typical_timeout = bridge_timeout.typical_seconds if bridge_timeout is not None else 15 * 60
        max_timeout = bridge_timeout.max_seconds if bridge_timeout is not None else 60 * 60
        distance_to_window_boundary = abs(event_timestamp - boundary)

        if distance_to_window_boundary <= typical_timeout:
            probability_score = 0.05 + (0.15 * distance_to_window_boundary / typical_timeout)
        elif distance_to_window_boundary <= max_timeout:
            typical_to_max_range = max(max_timeout - typical_timeout, 1)
            typical_overrun = distance_to_window_boundary - typical_timeout
            probability_score = 0.20 + (0.40 * typical_overrun / typical_to_max_range)
        else:
            max_overrun = distance_to_window_boundary - max_timeout
            probability_score = (
                0.60
                + min(
                    max_overrun / (3 * max_timeout),
                    1,
                )
                * 0.35
            )

        if probability_score < 0.30:
            label = "LOW"
        elif probability_score < 0.70:
            label = "MEDIUM"
        else:
            label = "HIGH"

        return (
            f"{label} ({probability_score:.0%}): event is "
            f"{distance_to_window_boundary}s from the {boundary_name} analysis-window "
            f"boundary; missing_side={missing_side or 'unknown'}; "
            f"bridge typical timeout={typical_timeout}s; "
            f"bridge max timeout={max_timeout}s."
        )

    def lock_without_mint(self, bridge: str) -> list[DetectionAlert]:
        """lock event without a corresponding mint event"""
        print("starting analysis for lock_without_mint")
        print("Ignoring this check for now, as it is not by itself an indicator of token theft")
        return []
        # TODO: check if proof was sent but no mint occured
        alerts = []

        tx_block_numbers, tx_timestamps = self._blockchain_transaction_context()

        for flow in self._configured_flows(bridge, "deposits"):
            grouped_events = self.fetch_event_pairs(bridge, flow)
            for correlation_id, events in grouped_events.items():
                if not (events["source"] and not events["destination"]):
                    continue
                for lock_event in self._unique_transaction_events(events["source"]):
                    event_timestamp = tx_timestamps.get(
                        lock_event.transaction_hash, lock_event.timestamp
                    )
                    event_block_number = tx_block_numbers.get(
                        lock_event.transaction_hash, lock_event.block_number
                    )
                    severity = AlertSeverity.MEDIUM
                    description_suffix = "No matching mint event was observed."
                    if self._event_is_recent(
                        bridge,
                        event_timestamp,
                        event_block_number,
                        getattr(lock_event, "blockchain", None),
                    ):
                        severity = AlertSeverity.LOW
                        description_suffix = "No matching mint event was observed yet, but the lock is still within the expected processing window."
                    probability = self._missing_pair_attack_probability(
                        bridge,
                        event_timestamp,
                        missing_side="destination",
                    )

                    alerts.append(
                        self.create_detection_alert(
                            signature_type=SignatureType.LOCK_WITHOUT_MINT,
                            severity=severity,
                            bridge=bridge,
                            correlation_id=correlation_id,
                            correlation_type=None,
                            src_event_id=lock_event.id,
                            dst_event_id=None,
                            title=f"{bridge}: lock event without corresponding mint event",
                            description=(
                                f"Found lock event {lock_event.event_type} with correlation_id={correlation_id}. "
                                f"Flow={flow.name}. "
                                f"{description_suffix}"
                            ),
                            created_at_ts=(
                                event_timestamp
                                if event_timestamp is not None
                                else lock_event.timestamp
                            ),
                            probability=probability,
                        )
                    )
                    print(
                        "[lock_without_mint] "
                        f"bridge={bridge} flow={flow.name} "
                        f"correlation_id={correlation_id} "
                        f"event_id={lock_event.id} tx_hash={lock_event.transaction_hash} "
                        f"event_type={lock_event.event_type} "
                        f"timestamp={event_timestamp} block_number={event_block_number} "
                        f"probability={probability}"
                    )
        print(f"cought {len(alerts)} alerts")
        return alerts

    def mint_without_lock(self, bridge: str) -> list[DetectionAlert]:
        print("starting analysis for mint_without_lock")
        alerts = []
        tx_block_numbers, tx_timestamps = self._blockchain_transaction_context()

        for flow in self._configured_flows(bridge, "deposits"):
            reverse_flow = EventPairFlow(
                name=flow.name,
                source=flow.destination,
                destination=flow.source,
                source_key=flow.destination_key,
                destination_key=flow.source_key,
            )
            grouped_events = self.fetch_event_pairs(bridge, reverse_flow)
            for correlation_id, events in grouped_events.items():
                if not (events["source"] and not events["destination"]):
                    continue
                for mint_event in self._unique_transaction_events(events["source"]):
                    event_timestamp = tx_timestamps.get(
                        mint_event.transaction_hash, mint_event.timestamp
                    )
                    event_block_number = tx_block_numbers.get(
                        mint_event.transaction_hash, mint_event.block_number
                    )
                    severity = AlertSeverity.HIGH
                    description_suffix = "No matching lock event was observed."
                    if self._event_is_recent(
                        bridge,
                        event_timestamp,
                        event_block_number,
                        getattr(mint_event, "blockchain", None),
                    ):
                        severity = AlertSeverity.MEDIUM
                        description_suffix = "No matching lock event was observed yet, but the mint is still within the expected processing window."
                    if (
                        bridge == "ccip"
                        and self._event_type_value(mint_event.event_type)
                        == "MESSAGE_EXECUTION_STATE_CHANGED"
                    ):
                        description_suffix += (
                            " In CCIP, ExecutionStateChanged is not exclusive to "
                            "completed cross-chain token movements, so this alert is "
                            "not by itself 100% evidence of an attack."
                        )
                    probability = self._missing_pair_attack_probability(
                        bridge,
                        event_timestamp,
                        missing_side="source",
                    )

                    alerts.append(
                        self.create_detection_alert(
                            signature_type=SignatureType.MINT_WITHOUT_LOCK,
                            severity=severity,
                            bridge=bridge,
                            correlation_id=correlation_id,
                            correlation_type=None,
                            src_event_id=None,
                            dst_event_id=mint_event.id,
                            title=f"{bridge}: mint event without corresponding lock event",
                            description=(
                                f"Found mint event {mint_event.event_type} with correlation_id={correlation_id}. "
                                f"Flow={flow.name}. "
                                f"{description_suffix}"
                            ),
                            created_at_ts=(
                                event_timestamp
                                if event_timestamp is not None
                                else mint_event.timestamp
                            ),
                            probability=probability,
                        )
                    )
                    print(
                        "[mint_without_lock] "
                        f"bridge={bridge} flow={flow.name} "
                        f"correlation_id={correlation_id} "
                        f"event_id={mint_event.id} tx_hash={mint_event.transaction_hash} "
                        f"event_type={mint_event.event_type} "
                        f"timestamp={event_timestamp} block_number={event_block_number} "
                        f"probability={probability}"
                    )
        print(f"cought {len(alerts)} alerts")
        return alerts
