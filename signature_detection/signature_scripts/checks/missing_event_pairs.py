from __future__ import annotations

from db.repository.detection_alert.detection_alert_model import DetectionAlert
from signature_detection.constants import AlertSeverity, EventPairFlow, SignatureType


class MissingEventPairsMixin:
    def lock_without_mint(self, bridge: str) -> list[DetectionAlert]:
        """lock event without a corresponding mint event"""
        print("starting analysis for lock_without_mint")
        # TODO: check if proof was sent but no mint occured
        alerts = []

        tx_block_numbers, tx_timestamps = self._blockchain_transaction_context()

        for flow in self._configured_flows(bridge, "deposits"):
            grouped_events = self.fetch_event_pairs(bridge, flow)
            for correlation_id, events in grouped_events.items():
                if not (events["source"] and not events["destination"]):
                    continue
                lock_event = self.pick_first(events["source"])

                # no lock event too, so keep going
                if lock_event is None:
                    continue

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
                ):
                    severity = AlertSeverity.LOW
                    description_suffix = "No matching mint event was observed yet, but the lock is still within the expected processing window."

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
                            event_timestamp if event_timestamp is not None else lock_event.timestamp
                        ),
                        probability="TODO",
                    )
                )
                print(
                    "[lock_without_mint] "
                    f"bridge={bridge} flow={flow.name} "
                    f"correlation_id={correlation_id} "
                    f"event_id={lock_event.id} tx_hash={lock_event.transaction_hash} "
                    f"event_type={lock_event.event_type} "
                    f"timestamp={event_timestamp} block_number={event_block_number}"
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
                mint_event = self.pick_first(events["source"])

                if mint_event is None:
                    continue

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
                ):
                    severity = AlertSeverity.MEDIUM
                    description_suffix = "No matching lock event was observed yet, but the mint is still within the expected processing window."

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
                            event_timestamp if event_timestamp is not None else mint_event.timestamp
                        ),
                        probability="TODO",
                    )
                )
                print(
                    "[mint_without_lock] "
                    f"bridge={bridge} flow={flow.name} "
                    f"correlation_id={correlation_id} "
                    f"event_id={mint_event.id} tx_hash={mint_event.transaction_hash} "
                    f"event_type={mint_event.event_type} "
                    f"timestamp={event_timestamp} block_number={event_block_number}"
                )
        print(f"cought {len(alerts)} alerts")
        return alerts
