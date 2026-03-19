from normalization.source_models.across import AcrossBlockchainTransaction


def get_across_tx_context(session, tx_hash: str):
    return (
        session.query(AcrossBlockchainTransaction)
        .filter(AcrossBlockchainTransaction.transaction_hash == tx_hash)
        .first()
    )