from db.database import get_session
from db.repository.bridge_tables.ronin import RoninBlockchainTransaction

class RoninBlockchainTransactionRepository:
    def get_all(self):
        # This method should return all cross-chain transactions for the Ronin bridge
        session = get_session()
        try:
            return (
                session.query(RoninBlockchainTransaction)
                .all()
            )
        finally:
            session.close()