from __future__ import annotations

from db.repository.detection_alert.detection_alert_model import DetectionAlert
from db.repository.normalized_event.normalized_event_model import NormalizedEvent
from db.repository.transfer_events.transfer_events_repository import (
    CCIPTransferRepository,
    CCTPTransferRepository,
    GenericTransferRepository,
    PolygonTransferRepository,
    RoninTransferRepository,
)
from signature_detection.constants import (
    TOKEN_CONTRACT_ATTACK_CONFIG,
    AlertSeverity,
    SignatureType,
    TokenContractAttackConfig,
)

TRANSFER_REPOSITORIES = {
    "across": GenericTransferRepository("across_transfers"),
    "ccip": CCIPTransferRepository,
    "cctp": CCTPTransferRepository,
    "debridge": GenericTransferRepository("debridge_transfers"),
    "mayan": GenericTransferRepository("mayan_transfers"),
    "meter.io": GenericTransferRepository("meter_io_transfers"),
    "omnibridge": GenericTransferRepository("omnibridge_transfers"),
    "polygon": PolygonTransferRepository,
    "qubit": GenericTransferRepository("qubit_transfers"),
    "ronin": RoninTransferRepository,
}


class TokenContractAttacksMixin:
    def token_contract_attacks(self) -> list[DetectionAlert]:
        """Check for token contract attacks. Search for discrepancies between lock/burn event and either the underlying tx (native token), or the corresponding transfer event (ERC20)"""
        print("starting analysis for token_contract_attacks")
        # 0 - get configs for bridge
        alerts: list[DetectionAlert] = []
        configs = TOKEN_CONTRACT_ATTACK_CONFIG.get(self.bridge, ())
        self._debug(f"token_contract_attacks: configs={len(configs)}")
        if not configs:
            print(f"cought {len(alerts)} alerts")
            return alerts

        # 1 - fetch lock/burn events
        blockchain_transactions = self._analysis_blockchain_transactions()
        txs_by_hash = {
            tx.transaction_hash: tx
            for tx in blockchain_transactions
            if tx.transaction_hash is not None
        }
        self._debug(
            "token_contract_attacks: "
            f"transactions={len(blockchain_transactions)} indexed_transactions={len(txs_by_hash)}"
        )

        transfers_by_tx: dict[str, list] = {}
        transfer_repository = TRANSFER_REPOSITORIES.get(self.bridge)
        if transfer_repository is not None:
            transfers = transfer_repository.get_all()
            for transfer in transfers:
                transfers_by_tx.setdefault(transfer.transaction_hash, []).append(transfer)
            self._debug(
                "token_contract_attacks: "
                f"transfers={len(transfers)} txs_with_transfers={len(transfers_by_tx)}"
            )
        else:
            self._debug("token_contract_attacks: no transfer repository configured")

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

                # 2 - for each event, check if it's native or ERC20 token
                tx = txs_by_hash.get(event.transaction_hash)
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

                self._debug(
                    "token_contract_attacks: result "
                    f"id={event.id} tx={event.transaction_hash} invalid_fields={invalid_fields}"
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

        print(f"cought {len(alerts)} alerts")
        return alerts

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
        if status is not None and status != "1":
            invalid_fields.append(
                f"3) transaction status is not success (status={status})"
            )

        return invalid_fields

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
        if status is not None and status != "1":
            invalid_fields.append(
                f"4) transaction status is not success (status={status})"
            )

        # check if the contract address of the event is official/correct
        invalid_fields.extend(self._check_expected_source_contract(event, config, 5))

        # check if a transfer event actually occurred
        if not transfers:
            invalid_fields.append(
                f"0) no ERC20 Transfer event found in the {config.event_label} transaction"
            )
            return invalid_fields

        # check:
        #   tokens match
        #   lock/burn's contract address is transfer's "to" address
        #   lock/burn's "from" is transfer's "from"
        #   lock/burn amount is transfer's amount
        matching_transfers = [
            transfer
            for transfer in transfers
            if self._normalized_value(transfer.token_address)
            == self._normalized_value(event.token_in)
            and self._normalized_value(transfer.to_address)
            == self._normalized_value(event.contract_address)
            and self._normalized_value(transfer.from_address)
            == self._normalized_value(event.actor_from)
            and transfer.amount == event.amount_in
        ]
        if matching_transfers:
            return invalid_fields

        ## tokens match
        transfer_invalid_fields = []
        token_transfers = [
            transfer
            for transfer in transfers
            if self._normalized_value(transfer.token_address)
            == self._normalized_value(event.token_in)
        ]
        token_transfers_from_actor = [
            transfer
            for transfer in token_transfers
            if self._normalized_value(transfer.from_address)
            == self._normalized_value(event.actor_from)
        ]
        has_transfer_to_contract = any(
            self._normalized_value(transfer.to_address)
            == self._normalized_value(event.contract_address)
            for transfer in token_transfers_from_actor
        )
        total_transferred_from_actor = sum(
            transfer.amount for transfer in token_transfers_from_actor
        )
        if has_transfer_to_contract and total_transferred_from_actor == event.amount_in:
            return invalid_fields

        ## lock/burn's contract address is transfer's "to" address
        if not has_transfer_to_contract:
            transfer_invalid_fields.append(
                f"1) no token Transfer to the {config.event_label} contract "
                f"(expected_to={event.contract_address or '<missing>'})"
            )

        ## lock/burn's "from" is transfer's "from"
        if not token_transfers_from_actor:
            transfer_invalid_fields.append(
                f"2) no token Transfer from the {config.actor_label} "
                f"(expected_from={event.actor_from or '<missing>'})"
            )

        ## lock/burn amount is transfer's amount
        if not any(transfer.amount == event.amount_in for transfer in token_transfers):
            transfer_invalid_fields.append(
                f"3) no token Transfer amount matches the {config.amount_label} "
                f"(expected_amount={event.amount_in})"
            )

        if not transfer_invalid_fields:
            transfer_invalid_fields.append(
                f"1) 2) 3) no single token Transfer matches all {config.event_label} checks"
            )

        return invalid_fields + transfer_invalid_fields
