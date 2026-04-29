from __future__ import annotations

from collections import defaultdict
from typing import List

from db.repository.blockchain_transactions.blockchain_transactions_repository import (
    RoninBlockchainTransactionRepository,
)
from db.repository.cross_chain_transactions.cross_chain_transactions_repository import (
    RoninCrossChainTransactionRepository,
)

from .analyser import Analyser
from db.repository.detection_alert.detection_alert_model import DetectionAlert

RONIN_SIGNATURE_THRESHOLD = 16  # TODO: this is a placeholder


class RoninAnalyser(Analyser):
    def __init__(self):
        super().__init__("ronin")

    def fetch_blockchain_transactions(self):
        return RoninBlockchainTransactionRepository.get_all()

    def fetch_blockchain_transactions_with_receipts_with_signatures(self):
        return (
            RoninBlockchainTransactionRepository.get_transactions_with_receipt_with_signatures()
        )

    def fetch_crosschain_transactions(self):
        return RoninCrossChainTransactionRepository.get_all()

    def analyse_cross_chain_transactions(self) -> List[DetectionAlert]:
        alerts = []

        # 0 - fetch cross-chain transactions
        crosschain_txs = self.fetch_crosschain_transactions()

        return alerts

        # 1 - check for token discrepancies
        for tx in crosschain_txs:
            if (
                tx.src_contract_address != tx.dst_source_contract_address
                or tx.src_destination_contract_address != tx.dst_contract_address
            ):
                pass  # TODO: raise alert

        # TODO: add more cctx checks

    def analyse_proofs(self) -> List[DetectionAlert]:
        alerts = []

        # 1 - fetch blockchain transactions
        receipt_txs = self.fetch_blockchain_transactions_with_receipts_with_signatures()

        # 2 - group
        receipts = defaultdict(list)
        for tx in receipt_txs:
            receipt = tx.decoded_input_data["_receipt"]

            receipt_key = (
                receipt["id"],
                receipt["kind"],
                receipt["info"]["quantity"],
                receipt["ronin"]["addr"],
                receipt["mainchain"]["addr"],
            )
            receipts[receipt_key].append(tx)

            # 3 - check duplicate signatures
            sigs = tx.decoded_input_data["_signatures"]

            seen = set()
            duplicates = False

            for sig in sigs:
                sig_tuple = (sig["r"], sig["s"], sig["v"])
                if sig_tuple in seen:
                    duplicates = True
                seen.add(sig_tuple)

            if duplicates:
                pass  # TODO: raise alert

            # 4 - check signature threshold
            if len(sigs) < RONIN_SIGNATURE_THRESHOLD:
                pass  # TODO: raise alert

        # 5 - same receipt used multiple times
        for key, txs in receipts.items():
            if len(txs) > 1:
                pass  # TODO: raise alert

        return alerts
