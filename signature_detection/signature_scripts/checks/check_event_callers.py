from __future__ import annotations

import json
from collections.abc import Iterable

from db.repository.detection_alert.detection_alert_model import DetectionAlert
from db.repository.normalized_event.normalized_event_model import NormalizedEvent
from signature_detection.constants import AlertSeverity, SignatureType

EXPECTED_EVENT_CALLERS: dict[str, dict[str, tuple[str, ...]]] = {}
DANGEROUS_TRACE_OPERATIONS = {"CREATE", "CREATE2", "SELFDESTRUCT"}


class CheckEventCallersMixin:
    def check_event_callers(self) -> list[DetectionAlert]:
        print("starting analysis for check_event_callers")

        alerts: list[DetectionAlert] = []
        transactions = self._analysis_blockchain_transactions()
        destination_events_by_tx = self._destination_events_by_transaction()

        for tx in transactions:

            # fetch calls from trace
            calls = self._calls_from_trace(getattr(tx, "calls", None))

            # normalize calls to make it more readable and easier to work with
            call_frames = self._transaction_root_frames(tx)
            call_frames.extend(self._iter_trace_calls(calls))
            if not call_frames:
                continue

            # check for dangerous operations, such as create and self destruct
            alerts.extend(self._check_dangerous_trace_operations(tx, call_frames))

            for event in destination_events_by_tx.get(tx.transaction_hash, []):
                alert = self._check_destination_event_caller(tx, event, call_frames)
                if alert is not None:
                    alerts.append(alert)

        print(f"cought {len(alerts)} alerts")
        return alerts

    def _destination_events_by_transaction(self) -> dict[str, list[NormalizedEvent]]:
        events_by_tx: dict[str, list[NormalizedEvent]] = {}
        seen_event_ids: set[int] = set()

        for flow_type in ("deposits", "withdrawals"):
            for flow in self._configured_flows(self.bridge, flow_type):
                for event in self._events_by_event_type(flow.destination, self.bridge):
                    if event.id in seen_event_ids:
                        continue
                    seen_event_ids.add(event.id)
                    events_by_tx.setdefault(event.transaction_hash, []).append(event)

        return events_by_tx

    def _calls_from_trace(self, trace) -> list[dict]:
        """Extract calls array from transaction trace"""
        if trace is None:
            return []

        if isinstance(trace, str):
            try:
                trace = json.loads(trace)
            except json.JSONDecodeError:
                self._debug("check_event_callers: transaction calls field is not valid JSON")
                return []

        if isinstance(trace, list):
            return [call for call in trace if isinstance(call, dict)]

        if not isinstance(trace, dict):
            return []

        if self._trace_node_type(trace) or trace.get("from") or trace.get("to"):
            return [trace]

        calls = trace.get("calls")
        if isinstance(calls, list):
            return [call for call in calls if isinstance(call, dict)]

        return []

    def _transaction_root_frames(self, tx) -> list[dict]:
        from_address = self._normalized_value(getattr(tx, "from_address", None))
        to_address = self._normalized_value(getattr(tx, "to_address", None))
        if from_address is None and to_address is None:
            return []

        return [
            {
                "call": None,
                "parent": None,
                "path": ("tx",),
                "depth": 0,
                "operation": "TX",
                "from": from_address,
                "to": to_address,
            }
        ]

    def _iter_trace_calls(
        self,
        calls: Iterable[dict],
        path: tuple[int, ...] = (),
        parent: dict | None = None,
    ):
        for index, call in enumerate(calls):
            call_path = path + (index,)
            yield {
                "call": call,
                "parent": parent,
                "path": call_path,
                "depth": len(call_path) - 1,
                "operation": self._trace_node_type(call),
                "from": self._normalized_value(call.get("from")),
                "to": self._normalized_value(call.get("to")),
            }
            child_calls = call.get("calls")
            if isinstance(child_calls, list):
                yield from self._iter_trace_calls(child_calls, call_path, call)

    def _trace_node_type(self, call: dict) -> str | None:
        operation = call.get("type") or call.get("callType") or call.get("op") or call.get("opcode")
        if operation is None:
            action = call.get("action")
            if isinstance(action, dict):
                operation = action.get("callType") or action.get("type")
        return str(operation).upper() if operation is not None else None

    def _expected_callers_for_event(self, event: NormalizedEvent) -> set[str]:
        bridge_callers = EXPECTED_EVENT_CALLERS.get(self.bridge, {})
        event_type = self._event_type_value(event.event_type)
        return {
            caller.lower() for caller in bridge_callers.get(event_type, ()) if caller is not None
        }

    def _find_event_call_frame(
        self, event: NormalizedEvent, call_frames: list[dict]
    ) -> dict | None:
        event_contract = self._normalized_value(event.contract_address)
        if event_contract is None:
            return None

        matching_frames = [frame for frame in call_frames if frame["to"] == event_contract]
        if not matching_frames:
            return None

        return max(
            matching_frames,
            key=lambda frame: (frame["depth"], 1 if frame["operation"] != "TX" else 0),
        )

    def _check_destination_event_caller(
        self,
        tx,
        event: NormalizedEvent,
        call_frames: list[dict],
    ) -> DetectionAlert | None:
        call_frame = self._find_event_call_frame(event, call_frames)
        if call_frame is None:
            self._debug(
                "check_event_callers: no trace frame matched "
                f"event_id={event.id} tx={event.transaction_hash} "
                f"contract={event.contract_address}"
            )
            return None

        caller = call_frame["from"]
        expected_callers = self._expected_callers_for_event(event)
        if caller in expected_callers:
            return None

        correlation_id = event.correlation_id or event.transaction_hash or str(event.raw_pk)
        expected = ", ".join(sorted(expected_callers)) if expected_callers else "<empty>"
        operation = call_frame["operation"] or "<unknown>"
        return self.create_detection_alert(
            signature_type=SignatureType.UNEXPECTED_EVENT_CALLER,
            severity=AlertSeverity.HIGH,
            bridge=self.bridge,
            correlation_id=correlation_id,
            correlation_type="event_caller",
            src_event_id=None,
            dst_event_id=event.id,
            title=f"{self.bridge}: unexpected destination event caller",
            description=(
                f"Found destination event {event.event_type} in tx={tx.transaction_hash} "
                f"emitted by contract={event.contract_address}. Trace frame type={operation} "
                f"has caller={caller or '<missing>'}; expected one of: {expected}."
            ),
            created_at_ts=self._created_at_ts_for_event(event),
            probability="TODO",
        )

    def _check_dangerous_trace_operations(
        self, tx, call_frames: list[dict]
    ) -> list[DetectionAlert]:
        dangerous_frames = [
            frame for frame in call_frames if frame["operation"] in DANGEROUS_TRACE_OPERATIONS
        ]
        if not dangerous_frames:
            return []

        operations = sorted({frame["operation"] for frame in dangerous_frames})
        frame_notes = [
            (
                f"{frame['operation']} from={frame['from'] or '<missing>'} "
                f"to={frame['to'] or '<missing>'} path={'.'.join(map(str, frame['path']))}"
            )
            for frame in dangerous_frames[:10]
        ]
        if len(dangerous_frames) > 10:
            frame_notes.append(f"... {len(dangerous_frames) - 10} more")

        return [
            self.create_detection_alert(
                signature_type=SignatureType.DANGEROUS_TRACE_OPERATION,
                severity=AlertSeverity.HIGH,
                bridge=self.bridge,
                correlation_id=tx.transaction_hash,
                correlation_type="trace_operations",
                src_event_id=None,
                dst_event_id=None,
                title=f"{self.bridge}: dangerous trace operation detected",
                description=(
                    f"Found potentially dangerous operation(s) in tx={tx.transaction_hash}: "
                    f"{', '.join(operations)}. Frames: {'; '.join(frame_notes)}."
                ),
                created_at_ts=getattr(tx, "timestamp", None),
                probability="TODO",
            )
        ]


"""
"calls": [
    {
      "from": "0x64192819ac13ef72bf6b5ae239ac672b43a9af08",
      "to": "0xd6c4986bbe09f2ddb262b4611b0ba06891be605e",
      "type": "DELEGATECALL",
      "value": "0x0",
      "calls": [
        {
          "from": "0x64192819ac13ef72bf6b5ae239ac672b43a9af08",
          "to": "0x88d100432f98956b16b66df56962fd3e5ccd297a",
          "type": "CALL",
          "input": "0x23b872dd...",
          "output": "0x0000000000000000000000000000000000000000000000000000000000000001",
          "value": "0x0"
        }
      ]
    }
  ]
"""
