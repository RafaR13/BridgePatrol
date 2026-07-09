from __future__ import annotations

from collections import defaultdict
import json
from typing import List

from db.repository.blockchain_transactions.blockchain_transactions_repository import (
    RoninBlockchainTransactionRepository,
)
from db.repository.transfer_events.transfer_events_repository import (
    RoninTransferRepository,
)
from normalization.event_types import NormalizedEventType

from .analyser import Analyser
from db.repository.detection_alert.detection_alert_model import DetectionAlert
from signature_detection.constants import (
    AlertSeverity,
    SignatureType,
)

RONIN_SIGNATURE_THRESHOLD = 16


class RoninAnalyser(Analyser):
    # RONIN_NATIVE_TOKEN = "TODO"
    # RONIN_MAINCHAIN_GATEWAY_CONTRACT = "0x64192819ac13ef72bf6b5ae239ac672b43a9af08"
    # RONIN_GATEWAY_CONTRACT = "0x0cf8ff40a508bdbc39fbe1bb679dcba64e65c7df"

    def __init__(self):
        super().__init__("ronin")

    def fetch_blockchain_transactions(self):
        return RoninBlockchainTransactionRepository.get_all()

    def fetch_blockchain_transactions_with_receipts_with_signatures(self):
        transactions = (
            RoninBlockchainTransactionRepository.get_transactions_with_receipt_with_signatures()
        )
        return self._filter_objects_for_analysis_window(transactions)

    def analyse_bridge_specific_signatures(self) -> List[DetectionAlert]:
        alerts = []
        alerts.extend(self.contract_discrepancies())
        alerts.extend(self.analyse_ronin_proofs())
        alerts.extend(self.token_contract_attacks())
        return alerts

    def bridge_specific_signature_checks(self):
        return (
            ("contract_discrepancies", self.contract_discrepancies, ()),
            ("ronin_proofs", self.analyse_ronin_proofs, ()),
            ("token_contract_attacks", self.token_contract_attacks, ()),
        )

    def _normalized_value(self, value):
        if value is None:
            return None
        return str(value).lower()

    def _receipt_key(self, receipt) -> tuple:
        info = receipt.get("info") or {}
        ronin = receipt.get("ronin") or {}
        mainchain = receipt.get("mainchain") or {}
        return (
            receipt.get("id"),
            receipt.get("kind"),
            info.get("quantity") if isinstance(info, dict) else None,
            ronin.get("addr") if isinstance(ronin, dict) else None,
            mainchain.get("addr") if isinstance(mainchain, dict) else None,
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
        decoded_input = {}
        # decoded_input = tx.decoded_input_data or {}
        if isinstance(decoded_input, str):
            try:
                decoded_input = json.loads(decoded_input)
            except json.JSONDecodeError:
                return {}
        if not isinstance(decoded_input, dict):
            return {}
        return decoded_input

    # contract mismatch attacks:
    def contract_discrepancies(self) -> List[DetectionAlert]:
        """Detect discrepancies in contract addresses between paired events of the same flow."""
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
                    source_token_in = self._normalized_value(source_event.token_in)
                    destination_token_in = self._normalized_value(destination_event.token_in)
                    if source_token_in != destination_token_in:
                        mismatches.append(
                            f"token_in source={source_event.token_in} destination={destination_event.token_in}"
                        )
                    source_token_out = self._normalized_value(source_event.token_out)
                    destination_token_out = self._normalized_value(destination_event.token_out)
                    if source_token_out != destination_token_out:
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
                            created_at_ts=(
                                self._created_at_ts_for_event(destination_event)
                                or self._created_at_ts_for_event(source_event)
                            ),
                            probability="TODO",
                        )
                    )

        return alerts

    # proof signature attacks:
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
            if not isinstance(sigs, list):
                sigs = []

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
                    tx.transaction_hash for tx in txs if tx.transaction_hash is not None
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

    """
    # token contract attacks:
    def _check_ronin_native_token(self, event, tx, expected_contract) -> list[str]:
        token contract checks regarding native tokens
        invalid_fields = []

        # 1) verificar se o "value" da transação é o mesmo do receipt.quantity
        if tx is None or tx.value != event.amount_in:
            invalid_fields.append(
                "1) tx.value does not match requested amount "
                f"(tx.value={getattr(tx, 'value', '<missing>')}, amount={event.amount_in})"
            )

        # 2) verificar se o receipt tokenAddr é o contract oficial da bridge
        if str(event.contract_address).lower() != expected_contract:
            invalid_fields.append(
                "2) event contract is not the official Ronin bridge "
                f"(contract={event.contract_address or '<missing>'}, expected={expected_contract})"
            )

        # 3) verificar se o status é success
        if str(event.status) != "1":
            invalid_fields.append(
                f"3) transaction status is not success (status={event.status or '<missing>'})"
            )

        return invalid_fields

    def _check_ronin_erc20_token(self, event, transfers) -> list[str]:
        token contract checks regarding ERC20 tokens
        invalid_fields = []

        # 0) Verificar se houve transfer event nesta transação
        if not transfers:
            return ["0) no ERC20 Transfer event found in the request transaction"]

        matching_transfers = [
            transfer
            for transfer in transfers
            if str(transfer.token_address).lower() == str(event.token_in).lower()
            and str(transfer.to_address).lower() == str(event.contract_address).lower()
            and str(transfer.from_address).lower() == str(event.actor_from).lower()
            and transfer.amount == event.amount_in
        ]
        if matching_transfers:
            return invalid_fields

        token_transfers = [
            transfer
            for transfer in transfers
            if str(transfer.token_address).lower() == str(event.token_in).lower()
        ]

        # 1) verificar se o transfer.to é o address do token
        if not any(
            str(transfer.to_address).lower() == str(event.contract_address).lower()
            for transfer in token_transfers
        ):
            invalid_fields.append(
                "1) no token Transfer to the request contract "
                f"(expected_to={event.contract_address or '<missing>'})"
            )

        # 2) verificar se o transfer.from é quem fez o request
        if not any(
            str(transfer.from_address).lower() == str(event.actor_from).lower()
            for transfer in token_transfers
        ):
            invalid_fields.append(
                "2) no token Transfer from the request actor "
                f"(expected_from={event.actor_from or '<missing>'})"
            )

        # 3) verificar se transfer.value é igual ao receipt.info.quantity
        if not any(transfer.amount == event.amount_in for transfer in token_transfers):
            invalid_fields.append(
                "3) no token Transfer amount matches the request amount "
                f"(expected_amount={event.amount_in})"
            )

        if not invalid_fields:
            invalid_fields.append("1) 2) 3) no single token Transfer matches all request checks")

        return invalid_fields

    '''
    def token_contract_attacks(self) -> list[DetectionAlert]:
        alerts: list[DetectionAlert] = []

        # 1 - fetch lock/burn events - DepositRequested and WithdrawalRequested for now, and corresponding transaction
        events = []
        events.extend(
            NormalizedEventRepository.get_events_by_event_type(
                NormalizedEventType.DEPOSIT_REQUESTED,
                self.bridge,
            )
        )
        events.extend(
            NormalizedEventRepository.get_events_by_event_type(
                NormalizedEventType.WITHDRAWAL_REQUESTED,
                self.bridge,
            )
        )
        txs_by_hash = {
            tx.transaction_hash: tx
            for tx in RoninBlockchainTransactionRepository.get_all()
            if tx.transaction_hash is not None
        }
        transfers_by_tx: dict[str, list] = {}
        for transfer in RoninTransferRepository.get_all():
            transfers_by_tx.setdefault(transfer.transaction_hash, []).append(transfer)

        # 2 - for each event, check if it's native or ERC20 token
        for event in events:
            tx = txs_by_hash.get(event.transaction_hash)
            expected_contract = (
                self.RONIN_MAINCHAIN_GATEWAY_CONTRACT
                if event.event_type == NormalizedEventType.DEPOSIT_REQUESTED
                else self.RONIN_GATEWAY_CONTRACT
            )

            if str(event.token_in).lower() == self.RONIN_NATIVE_TOKEN.lower():
                invalid_fields = self._check_ronin_native_token(event, tx, expected_contract)
            else:
                invalid_fields = self._check_ronin_erc20_token(
                    event,
                    transfers_by_tx.get(event.transaction_hash, []),
                )
                if str(event.contract_address).lower() != expected_contract:
                    invalid_fields.append(
                        "4) event contract is not the expected Ronin bridge "
                        f"(contract={event.contract_address or '<missing>'}, expected={expected_contract})"
                    )

            if not invalid_fields:
                continue

            correlation_id = event.correlation_id or event.transaction_hash or str(event.raw_pk)
            alerts.append(
                self.create_detection_alert(
                    signature_type=SignatureType.CONTRACT_MISMATCH,
                    severity=AlertSeverity.HIGH,
                    bridge=self.bridge,
                    correlation_id=correlation_id,
                    correlation_type="ronin_token_contract_attack",
                    src_event_id=event.id,
                    dst_event_id=None,
                    title="ronin: request event failed token contract checks",
                    description=(
                        f"Found {event.event_type} event with correlation_id={correlation_id}. "
                        f"Invalid token contract fields: {'; '.join(invalid_fields)}."
                    ),
                    created_at_ts=event.timestamp,
                    probability="TODO",
                )
            )

        return alerts
    '''
    """
