from db.database import get_session
from db.repository.bridge_tables.ronin import RoninBlockchainTransaction

class RoninBlockchainTransactionRepository:
    def get_all(self):
        session = get_session()
        try:
            return (
                session.query(RoninBlockchainTransaction)
                .all()
            )
        finally:
            session.close()
    
    def get_transactions_with_receipt_with_signatures(self):
        session = get_session()
        try:
            return (
                session.query(RoninBlockchainTransaction)
                .filter(
                    RoninBlockchainTransaction.decoded_input_data.ilike("%_receipt%"),
                    RoninBlockchainTransaction.decoded_input_data.ilike("%_signatures%")
                )
                .all()
            )
        finally:
            session.close()
