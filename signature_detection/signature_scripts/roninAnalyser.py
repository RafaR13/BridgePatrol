from __future__ import annotations

from collections import defaultdict
import json
from typing import List

from db.repository.blockchain_transactions.blockchain_transactions_repository import (
    RoninBlockchainTransactionRepository,
)
from db.repository.cross_chain_transactions.cross_chain_transactions_repository import (
    RoninCrossChainTransactionRepository,
)

from .analyser import Analyser
from db.repository.detection_alert.detection_alert_model import DetectionAlert
from signature_detection.constants import (
    AlertSeverity,
    SignatureType,
)

RONIN_SIGNATURE_THRESHOLD = 16


class RoninAnalyser(Analyser):
    def __init__(self):
        super().__init__("ronin")

    def fetch_blockchain_transactions(self):
        return RoninBlockchainTransactionRepository.get_all()

    def fetch_blockchain_transactions_with_receipts_with_signatures(self):
        return RoninBlockchainTransactionRepository.get_transactions_with_receipt_with_signatures()

    def fetch_crosschain_transactions(self):
        return RoninCrossChainTransactionRepository.get_all()

    def analyse_bridge_specific_signatures(self) -> List[DetectionAlert]:
        alerts = []
        alerts.extend(self.contract_discrepancies())
        alerts.extend(self.analyse_ronin_proofs())
        return alerts

    def _normalized_value(self, value):
        if value is None:
            return None
        return str(value).lower()

    def _receipt_key(self, receipt) -> tuple:
        return (
            receipt.get("id"),
            receipt.get("kind"),
            receipt.get("info", {}).get("quantity"),
            receipt.get("ronin", {}).get("addr"),
            receipt.get("mainchain", {}).get("addr"),
        )

    def _receipt_correlation_id(self, receipt_key: tuple) -> str:
        receipt_id = receipt_key[0]
        if receipt_id is not None:
            return str(receipt_id)[:128]
        return json.dumps(receipt_key, default=str, ensure_ascii=False)[:128]

    def _signature_tuple(self, signature) -> tuple:
        if not isinstance(signature, dict):
            return (str(signature), None, None)
        return (
            signature.get("r"),
            signature.get("s"),
            signature.get("v"),
        )

    def _decoded_input(self, tx) -> dict:
        decoded_input = tx.decoded_input_data or {}
        if isinstance(decoded_input, str):
            try:
                decoded_input = json.loads(decoded_input)
            except json.JSONDecodeError:
                return {}
        if not isinstance(decoded_input, dict):
            return {}
        return decoded_input

    def contract_discrepancies(self) -> List[DetectionAlert]:
        alerts = []

        for flow_type in ("deposits", "withdrawals"):
            for flow in self._configured_flows(self.bridge, flow_type):
                grouped_events = self.fetch_event_pairs(self.bridge, flow)

                for correlation_id, events in grouped_events.items():
                    source_event = self.pick_first(events["source"])
                    destination_event = self.pick_first(events["destination"])
                    if source_event is None or destination_event is None:
                        continue

                    mismatches = []
                    if self._normalized_value(source_event.token_in) != self._normalized_value(
                        destination_event.token_in
                    ):
                        mismatches.append(
                            f"token_in source={source_event.token_in} destination={destination_event.token_in}"
                        )
                    if self._normalized_value(source_event.token_out) != self._normalized_value(
                        destination_event.token_out
                    ):
                        mismatches.append(
                            f"token_out source={source_event.token_out} destination={destination_event.token_out}"
                        )

                    if not mismatches:
                        continue

                    alerts.append(
                        self.create_detection_alert(
                            signature_type=SignatureType.CONTRACT_MISMATCH,
                            severity=AlertSeverity.HIGH,
                            bridge=self.bridge,
                            correlation_id=correlation_id,
                            correlation_type=flow.name,
                            src_event_id=source_event.id,
                            dst_event_id=destination_event.id,
                            title="ronin: contract mismatch between paired events",
                            description=(
                                f"Found Ronin {flow.name} pair with inconsistent token contracts "
                                f"for correlation_id={correlation_id}: {'; '.join(mismatches)}."
                            ),
                            created_at_ts=destination_event.timestamp
                            or source_event.timestamp,
                            probability="TODO",
                        )
                    )

        return alerts

    def analyse_ronin_proofs(self) -> List[DetectionAlert]:
        alerts = []

        receipt_txs = self.fetch_blockchain_transactions_with_receipts_with_signatures()

        receipts = defaultdict(list)
        for tx in receipt_txs:
            decoded_input = self._decoded_input(tx)
            receipt = decoded_input.get("_receipt")
            sigs = decoded_input.get("_signatures") or []
            if not isinstance(receipt, dict):
                continue

            receipt_key = self._receipt_key(receipt)
            correlation_id = self._receipt_correlation_id(receipt_key)
            receipts[receipt_key].append(tx)

            seen = set()
            duplicate_signatures = set()

            for sig in sigs:
                sig_tuple = self._signature_tuple(sig)
                if sig_tuple in seen:
                    duplicate_signatures.add(sig_tuple)
                seen.add(sig_tuple)

            if duplicate_signatures:
                alerts.append(
                    self.create_detection_alert(
                        signature_type=SignatureType.DUPLICATE_SIGNATURE,
                        severity=AlertSeverity.HIGH,
                        bridge=self.bridge,
                        correlation_id=correlation_id,
                        correlation_type="ronin_proof",
                        src_event_id=None,
                        dst_event_id=None,
                        title="ronin: duplicate proof signatures detected",
                        description=(
                            f"Transaction {tx.transaction_hash} contains "
                            f"{len(duplicate_signatures)} duplicated validator signature(s) "
                            f"for receipt={correlation_id}."
                        ),
                        created_at_ts=tx.timestamp,
                        probability="TODO",
                    )
                )

            if len(sigs) < RONIN_SIGNATURE_THRESHOLD:
                alerts.append(
                    self.create_detection_alert(
                        signature_type=SignatureType.INSUFFICIENT_SIGNATURES,
                        severity=AlertSeverity.CRITICAL,
                        bridge=self.bridge,
                        correlation_id=correlation_id,
                        correlation_type="ronin_proof",
                        src_event_id=None,
                        dst_event_id=None,
                        title="ronin: proof has fewer signatures than required",
                        description=(
                            f"Transaction {tx.transaction_hash} contains {len(sigs)} "
                            f"signature(s) for receipt={correlation_id}; expected at least "
                            f"{RONIN_SIGNATURE_THRESHOLD}."
                        ),
                        created_at_ts=tx.timestamp,
                        probability="TODO",
                    )
                )

        for receipt_key, txs in receipts.items():
            if len(txs) > 1:
                tx_hashes = sorted(
                    tx.transaction_hash
                    for tx in txs
                    if tx.transaction_hash is not None
                )
                correlation_id = self._receipt_correlation_id(receipt_key)
                for tx in txs:
                    alerts.append(
                        self.create_detection_alert(
                            signature_type=SignatureType.RECEIPT_REPLAY,
                            severity=AlertSeverity.CRITICAL,
                            bridge=self.bridge,
                            correlation_id=correlation_id,
                            correlation_type="ronin_proof",
                            src_event_id=None,
                            dst_event_id=None,
                            title="ronin: same receipt used by multiple transactions",
                            description=(
                                f"Receipt={correlation_id} appears in multiple Ronin proof "
                                f"transactions: {', '.join(tx_hashes)}."
                            ),
                            created_at_ts=tx.timestamp,
                            probability="TODO",
                        )
                    )

        return alerts
