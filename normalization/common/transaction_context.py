from db.repository.bridge_tables.across import AcrossBlockchainTransactions
from db.repository.bridge_tables.ccip import CCIPBlockchainTransactions
from db.repository.bridge_tables.cctp import CCTPBlockchainTransactions
from db.repository.bridge_tables.debridge import DeBridgeBlockchainTransactions

"""from db.repository.bridge_tables.manual import (
    MeterIoBlockchainTransactions,
    QubitBlockchainTransactions,
    ThorchainBlockchainTransactions,
)"""
from db.repository.bridge_tables.mayan import MayanBlockchainTransactions
from db.repository.bridge_tables.nomad import NomadBlockchainTransactions
from db.repository.bridge_tables.omnibridge import OmnibridgeBlockchainTransactions
from db.repository.bridge_tables.polygon import PolygonBlockchainTransactions
from db.repository.bridge_tables.ronin import RoninBlockchainTransactions

TX_CONTEXT_MODELS = {
    "across": AcrossBlockchainTransactions,
    "ccip": CCIPBlockchainTransactions,
    "cctp": CCTPBlockchainTransactions,
    "debridge": DeBridgeBlockchainTransactions,
    "mayan": MayanBlockchainTransactions,
    "nomad": NomadBlockchainTransactions,
    # "meter.io": MeterIoBlockchainTransactions,
    "omnibridge": OmnibridgeBlockchainTransactions,
    "polygon": PolygonBlockchainTransactions,
    # "qubit": QubitBlockchainTransactions,
    "ronin": RoninBlockchainTransactions,
    # "thorchain": ThorchainBlockchainTransactions,
}
# NOTE: commented bridges are the ones where we manually added data, so normalization isn't necessary. If, in the future, we add support for these bridges in XChainDataGen, then uncomment


def get_tx_context(session, tx_hash: str, bridge: str):
    model = TX_CONTEXT_MODELS.get(bridge)
    if model is None:
        return None
    return get_bridge_tx_context(session, tx_hash, model)


def get_bridge_tx_context(session, tx_hash: str, model):
    return session.query(model).filter(model.transaction_hash == tx_hash).first()
