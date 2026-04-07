from db.repository.bridge_tables.ronin import RoninBlockchainTransaction
from db.repository.bridge_tables.across import AcrossBlockchainTransaction

def get_tx_context(session, tx_hash: str, bridge: str):
    if bridge == "across":
        return get_across_tx_context(session, tx_hash)
    if bridge == "ronin":
        return get_ronin_tx_context(session, tx_hash)
    return None

def get_across_tx_context(session, tx_hash: str):
    return (
        session.query(AcrossBlockchainTransaction)
        .filter(AcrossBlockchainTransaction.transaction_hash == tx_hash)
        .first()
    )

def get_ronin_tx_context(session, tx_hash: str):
    return (session.query(RoninBlockchainTransaction)
            .filter(RoninBlockchainTransaction.transaction_hash == tx_hash)
            .first()
            )