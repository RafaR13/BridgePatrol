from __future__ import annotations

from decimal import Decimal

from db.repository.detection_alert.detection_alert_model import DetectionAlert
from db.repository.normalized_event.normalized_event_model import NormalizedEvent
from db.repository.transfer_events.transfer_events_repository import TransferRepository
from normalization.event_types import NormalizedEventType
from signature_detection.constants import (
    TOKEN_CONTRACT_ATTACK_CONFIG,
    AlertSeverity,
    SignatureType,
    TokenContractAttackConfig,
)


MANUAL_NORMALIZED_TRANSFER_BRIDGES = {
    "meter.io",
    "pnetwork",
    "qubit",
    "thorchain",
}
TRANSFER_REPOSITORIES = {
    "across": TransferRepository("across_transfers"),
    "ccip": TransferRepository("ccip_transfers"),
    "cctp": TransferRepository("cctp_transfers"),
    "debridge": TransferRepository("debridge_transfers"),
    "mayan": TransferRepository("mayan_transfers"),
    "omnibridge": TransferRepository("omnibridge_transfers"),
    "polygon": TransferRepository("polygon_transfers"),
    "ronin": TransferRepository("ronin_transfers"),
}


class TokenContractAttacksMixin:
    def token_contract_attacks(self) -> list[DetectionAlert]:
        """Check for token contract attacks. Search for discrepancies between lock/burn event and either the underlying tx (native token), or the corresponding transfer event (ERC20)"""
        print("starting analysis for token_contract_attacks")
        # 0 - get configs for bridge
        alerts: list[DetectionAlert] = []
        skipped_missing_address: set[str] = set()
        configs = TOKEN_CONTRACT_ATTACK_CONFIG.get(self.bridge, ())
        self._debug(f"token_contract_attacks: configs={len(configs)}")
        if not configs:
            print(f"cought {len(alerts)} alerts")
            return alerts

        # 1 - fetch lock/burn events
        blockchain_transactions = self._analysis_blockchain_transactions()
        txs_by_hash = self._analysis_blockchain_transactions_by_hash()
        self._debug(
            "token_contract_attacks: "
            f"transactions={len(blockchain_transactions)} indexed_transactions={len(txs_by_hash)}"
        )

        transfers_by_tx = self._transfers_for_token_contract_checks_by_transaction_hash()
        self._debug(
            "token_contract_attacks: "
            f"txs_with_transfers={len(transfers_by_tx)}"
        )

        for config in configs:
            events = self._events_by_event_type(
                config.event_type,
                self.bridge,
            )
            self._debug(
                "token_contract_attacks: "
                f"config={config.event_label} event_type={config.event_type} events={len(events)}"
            )
            for event in events:
                if (
                    self.DEBUG_TRANSACTION_HASH
                    and event.transaction_hash != self.DEBUG_TRANSACTION_HASH
                ):
                    continue

                if event.token_in is None or event.amount_in is None:
                    self._debug(
                        "token_contract_attacks: skip event "
                        f"id={event.id} tx={event.transaction_hash} "
                        f"token_in={event.token_in} amount_in={event.amount_in}"
                    )
                    continue

                if self._normalized_value(event.contract_address) is None:
                    skipped_missing_address.add(self._event_analysis_key(event))
                    self._debug(
                        "token_contract_attacks: skip event missing contract_address "
                        f"id={event.id} tx={event.transaction_hash} "
                        f"cctx_id={event.cctx_id} correlation_id={event.correlation_id}"
                    )
                    continue

                # 2 - for each event, check if it's native or ERC20 token
                tx = txs_by_hash.get(event.transaction_hash)
                amount_invalid_fields: list[str] = []
                if self._is_native_token(event, config):
                    self._debug(
                        "token_contract_attacks: native check "
                        f"id={event.id} tx={event.transaction_hash} "
                        f"token={event.token_in} amount={event.amount_in} "
                        f"event_contract={event.contract_address} tx_found={tx is not None}"
                    )
                    invalid_fields = self._check_native_token_contract(event, tx, config)
                else:
                    event_transfers = transfers_by_tx.get(event.transaction_hash, [])
                    self._debug(
                        "token_contract_attacks: erc20 check "
                        f"id={event.id} tx={event.transaction_hash} "
                        f"token={event.token_in} amount={event.amount_in} "
                        f"actor_from={event.actor_from} event_contract={event.contract_address} "
                        f"transfers={len(event_transfers)}"
                    )
                    invalid_fields = self._check_erc20_token_contract(
                        event,
                        event_transfers,
                        config,
                        tx,
                    )
                    invalid_fields, amount_invalid_fields = (
                        self._split_amount_mismatch_fields(invalid_fields)
                    )

                self._debug(
                    "token_contract_attacks: result "
                    f"id={event.id} tx={event.transaction_hash} invalid_fields={invalid_fields}"
                )
                if not invalid_fields:
                    if amount_invalid_fields:
                        correlation_id = (
                            event.correlation_id or event.transaction_hash or str(event.raw_pk)
                        )
                        alerts.append(
                            self.create_detection_alert(
                                signature_type=SignatureType.AMOUNT_MISMATCH,
                                severity=AlertSeverity.HIGH,
                                bridge=self.bridge,
                                correlation_id=correlation_id,
                                correlation_type=config.correlation_type,
                                src_event_id=event.id,
                                dst_event_id=None,
                                title=f"{self.bridge}: {config.event_label} amount mismatch",
                                description=(
                                    f"Found {config.event_label} event with "
                                    f"correlation_id={correlation_id}. "
                                    f"Invalid amount fields: {'; '.join(amount_invalid_fields)}."
                                ),
                                created_at_ts=self._created_at_ts_for_event(event),
                                probability="TODO",
                            )
                        )
                    continue

                correlation_id = event.correlation_id or event.transaction_hash or str(event.raw_pk)
                alerts.append(
                    self.create_detection_alert(
                        signature_type=SignatureType.CONTRACT_MISMATCH,
                        severity=AlertSeverity.HIGH,
                        bridge=self.bridge,
                        correlation_id=correlation_id,
                        correlation_type=config.correlation_type,
                        src_event_id=event.id,
                        dst_event_id=None,
                        title=config.title,
                        description=(
                            f"Found {config.event_label} event with "
                            f"correlation_id={correlation_id}. "
                            f"Invalid token contract fields: {'; '.join(invalid_fields)}."
                        ),
                        created_at_ts=self._created_at_ts_for_event(event),
                        probability="TODO",
                    )
                )
                if amount_invalid_fields:
                    alerts.append(
                        self.create_detection_alert(
                            signature_type=SignatureType.AMOUNT_MISMATCH,
                            severity=AlertSeverity.HIGH,
                            bridge=self.bridge,
                            correlation_id=correlation_id,
                            correlation_type=config.correlation_type,
                            src_event_id=event.id,
                            dst_event_id=None,
                            title=f"{self.bridge}: {config.event_label} amount mismatch",
                            description=(
                                f"Found {config.event_label} event with "
                                f"correlation_id={correlation_id}. "
                                f"Invalid amount fields: {'; '.join(amount_invalid_fields)}."
                            ),
                            created_at_ts=self._created_at_ts_for_event(event),
                            probability="TODO",
                        )
                    )
                print(
                    "[token_contract_attacks] "
                    f"bridge={self.bridge} config={config.event_label} "
                    f"correlation_id={correlation_id} "
                    f"event_id={event.id} tx_hash={event.transaction_hash} "
                    f"event_type={event.event_type} "
                    f"token={event.token_in or '<missing>'} "
                    f"amount={event.amount_in if event.amount_in is not None else '<missing>'} "
                    f"event_contract={event.contract_address or '<missing>'} "
                    f"invalid_fields={'; '.join(invalid_fields)}"
                )

        if skipped_missing_address:
            print(
                "[token_contract_attacks] "
                f"{len(skipped_missing_address)} cctx could not be analyzed for this "
                "check because the normalized event contract address is missing."
            )
        print(f"cought {len(alerts)} alerts")
        return alerts

    def _event_analysis_key(self, event: NormalizedEvent) -> str:
        return str(
            event.cctx_id
            or event.correlation_id
            or event.transaction_hash
            or event.raw_pk
            or event.id
        )

    def _is_native_token(
        self,
        event: NormalizedEvent,
        config: TokenContractAttackConfig,
    ) -> bool:
        blockchain = self._normalized_value(event.blockchain) or self._normalized_value(
            event.src_blockchain
        )
        native_token = config.native_tokens.get(blockchain) if blockchain else None
        if native_token is None:
            return False

        return self._normalized_value(event.token_in) == self._normalized_value(native_token)

    def _expected_contract_values(self, config: TokenContractAttackConfig) -> set[str]:
        return {contract.lower() for contract in config.expected_contracts}

    def _status_value(self, event: NormalizedEvent, tx) -> str | None:
        status = event.status if event.status is not None else getattr(tx, "status", None)
        return str(status) if status is not None else None

    def _status_is_success(self, status: str | None) -> bool:
        if status is None:
            return True
        return status.strip().lower() in {"1", "success", "successful", "true"}

    def _check_expected_source_contract(
        self,
        event: NormalizedEvent,
        config: TokenContractAttackConfig,
        check_number: int,
    ) -> list[str]:
        expected_contracts = self._expected_contract_values(config)
        if not expected_contracts:
            return []

        event_contract = self._normalized_value(event.contract_address)
        if event_contract in expected_contracts:
            return []

        expected = ", ".join(sorted(expected_contracts))
        return [
            f"{check_number}) {config.event_label} contract is not an expected "
            f"{self.bridge} source contract "
            f"(contract={event.contract_address or '<missing>'}, expected={expected})"
        ]

    def _check_native_token_contract(
        self,
        event: NormalizedEvent,
        tx,
        config: TokenContractAttackConfig,
    ) -> list[str]:
        invalid_fields = []

        tx_value = getattr(tx, "value", None)
        if tx is not None and tx_value is not None and tx_value != event.amount_in:
            invalid_fields.append(
                f"1) tx.value does not match {config.amount_label} "
                f"(tx.value={tx_value}, amount={event.amount_in})"
            )

        invalid_fields.extend(self._check_expected_source_contract(event, config, 2))

        status = self._status_value(event, tx)
        if not self._status_is_success(status):
            invalid_fields.append(
                f"3) transaction status is not success (status={status})"
            )

        return invalid_fields

    def _split_amount_mismatch_fields(
        self,
        invalid_fields: list[str],
    ) -> tuple[list[str], list[str]]:
        contract_fields = []
        amount_fields = []
        for field in invalid_fields:
            if field.startswith("AMOUNT_MISMATCH:"):
                amount_fields.append(field.removeprefix("AMOUNT_MISMATCH:").strip())
            else:
                contract_fields.append(field)
        return contract_fields, amount_fields

    def _check_erc20_token_contract(
        self,
        event: NormalizedEvent,
        transfers: list,
        config: TokenContractAttackConfig,
        tx,
    ) -> list[str]:
        invalid_fields = []

        # check if tx status is sucess
        status = self._status_value(event, tx)
        if not self._status_is_success(status):
            invalid_fields.append(
                f"4) transaction status is not success (status={status})"
            )

        # check if the contract address of the event is official/correct
        invalid_fields.extend(self._check_expected_source_contract(event, config, 5))

        # check if a transfer event actually occurred
        if not transfers:
            native_value_fields = self._check_native_tx_value_without_transfer(
                event,
                tx,
                config,
            )
            if native_value_fields is not None:
                return invalid_fields + native_value_fields
            invalid_fields.append(
                f"0) no ERC20 Transfer event found in the {config.event_label} transaction"
            )
            return invalid_fields

        # check:
        #   tokens match
        #   transfer "to" is intentionally not checked here: for burn/redeem flows
        #   it can be a zero/dead/sink address, and in several datasets
        #   event.contract_address is the event emitter rather than the token recipient.
        #   lock/burn's "from" is transfer's "from"
        #   lock/burn amount is transfer's amount
        matching_transfers = [
            transfer
            for transfer in transfers
            if self._normalized_value(self._transfer_token_address(transfer))
            == self._normalized_value(event.token_in)
            # and self._normalized_value(self._transfer_to_address(transfer))
            # == self._normalized_value(event.contract_address)
            and self._normalized_value(self._transfer_from_address(transfer))
            == self._normalized_value(event.actor_from)
            and self._transfer_amount(transfer) == event.amount_in
        ]
        if matching_transfers:
            return invalid_fields

        ## tokens match
        transfer_invalid_fields = []
        token_transfers = [
            transfer
            for transfer in transfers
            if self._normalized_value(self._transfer_token_address(transfer))
            == self._normalized_value(event.token_in)
        ]
        token_transfers_from_actor = [
            transfer
            for transfer in token_transfers
            if self._normalized_value(self._transfer_from_address(transfer))
            == self._normalized_value(event.actor_from)
        ]
        total_transferred_from_actor = sum(
            self._transfer_amount(transfer) for transfer in token_transfers_from_actor
        )
        if total_transferred_from_actor == event.amount_in:
            return invalid_fields

        ## lock/deposit's contract address is transfer's "to" address
        # if not any(
        #     self._normalized_value(self._transfer_to_address(transfer))
        #     == self._normalized_value(event.contract_address)
        #     for transfer in token_transfers_from_actor
        # ):
        #     transfer_invalid_fields.append(
        #         f"1) no token Transfer to the {config.event_label} contract "
        #         f"(expected_to={event.contract_address or '<missing>'})"
        #     )

        ## lock/burn's "from" is transfer's "from"
        if not token_transfers_from_actor:
            transfer_invalid_fields.append(
                f"2) no token Transfer from the {config.actor_label} "
                f"(expected_from={event.actor_from or '<missing>'})"
            )

        ## lock/burn amount is transfer's amount
        if not any(
            self._transfer_amount(transfer) == event.amount_in
            for transfer in token_transfers
        ):
            transfer_invalid_fields.append(
                f"3) no token Transfer amount matches the {config.amount_label} "
                f"(expected_amount={event.amount_in})"
            )

        if not transfer_invalid_fields:
            transfer_invalid_fields.append(
                f"1) 2) 3) no single token Transfer matches all {config.event_label} checks"
            )

        return invalid_fields + transfer_invalid_fields

    def _check_native_tx_value_without_transfer(
        self,
        event: NormalizedEvent,
        tx,
        config: TokenContractAttackConfig,
    ) -> list[str] | None:
        tx_value = getattr(tx, "value", None)
        if tx is None or tx_value is None:
            return None

        tx_value = self._decimal_or_none(tx_value)
        event_amount = self._decimal_or_none(event.amount_in)
        if tx_value is None or tx_value == 0:
            return None

        if event_amount is not None and tx_value == event_amount:
            return []

        return [
            "AMOUNT_MISMATCH: "
            f"tx.value does not match {config.amount_label} "
            f"(tx.value={tx_value}, amount={event.amount_in})"
        ]

    def _decimal_or_none(self, value) -> Decimal | None:
        if value is None:
            return None
        return Decimal(str(value))

    def _transfers_for_token_contract_checks_by_transaction_hash(self) -> dict[str, list]:
        if self.bridge in MANUAL_NORMALIZED_TRANSFER_BRIDGES:
            return self._normalized_transfers_by_transaction_hash()

        transfer_repository = TRANSFER_REPOSITORIES.get(self.bridge)
        if transfer_repository is None:
            self._debug("token_contract_attacks: no transfer repository configured")
            return {}

        return self._transfers_by_transaction_hash(transfer_repository)

    def _normalized_transfers_by_transaction_hash(self) -> dict[str, list[NormalizedEvent]]:
        transfers_by_tx: dict[str, list[NormalizedEvent]] = {}
        for transfer in self._events_by_event_type(NormalizedEventType.TRANSFER, self.bridge):
            if transfer.transaction_hash is None:
                continue
            transfers_by_tx.setdefault(transfer.transaction_hash, []).append(transfer)
        return transfers_by_tx

    def _transfer_token_address(self, transfer):
        return (
            getattr(transfer, "token_address", None)
            or getattr(transfer, "token_in", None)
            or getattr(transfer, "token_out", None)
            or getattr(transfer, "contract_address", None)
        )

    def _transfer_from_address(self, transfer):
        return getattr(transfer, "from_address", None) or getattr(transfer, "actor_from", None)

    def _transfer_to_address(self, transfer):
        return getattr(transfer, "to_address", None) or getattr(transfer, "actor_to", None)

    def _transfer_amount(self, transfer):
        for field in ("amount", "amount_in", "amount_out"):
            value = getattr(transfer, field, None)
            if value is not None:
                return value
        return None
