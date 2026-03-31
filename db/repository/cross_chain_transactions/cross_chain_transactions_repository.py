from db.database import get_session
from normalization.source_models import RoninCrossChainTransaction

class RoninCrossChainTransactionRepository:
    def get_all(self):
        # This method should return all cross-chain transactions for the Ronin bridge
        session = get_session()
        try:
            return (
                session.query(RoninCrossChainTransaction)
                .all()
            )
        finally:
            session.close()