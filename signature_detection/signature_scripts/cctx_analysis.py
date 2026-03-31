from db.repository.cross_chain_transactions.cross_chain_transactions_repository import RoninCrossChainTransactionRepository

def proof_replay_cctx_level(bridge: str):
    # 1: get cctxx for bridge
    cctxs = RoninCrossChainTransactionRepository().get_all()
    # 2: group them by id (deposit id)
    # 3:for each group, check if multiple deposit id's
        # have same destination hash, amount, timestamp (with some tolerance), and recipient address
    # 4: if so, alert


def check_all_signatures(bridge: str):
    alerts = []
    
    alerts.extend(proof_replay_cctx_level(bridge))

    return alerts