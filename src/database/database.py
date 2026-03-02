from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base, CrossChainTx

class DBManager:
    def __init__(self, connection_string):
        self.engine = create_engine(connection_string)
        self.Session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine) # Cria as tabelas se não existirem

    def get_session(self):
        return self.Session()

    def upsert_cctx(self, cctx_id, bridge_name, **kwargs):
        """
        Insere uma nova CCTX ou atualiza uma existente.
        Essencial para ligar a origem ao destino em momentos diferentes.
        """
        session = self.get_session()
        try:
            tx = session.query(CrossChainTx).filter_by(cctx_id=cctx_id).first()
            if not tx:
                tx = CrossChainTx(cctx_id=cctx_id, bridge_name=bridge_name)
                session.add(tx)
            
            # Atualiza apenas os campos passados (src_..., dst_..., status, etc.)
            for key, value in kwargs.items():
                setattr(tx, key, value)
            
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Error on upsert: {e}")
            raise
        finally:
            session.close()