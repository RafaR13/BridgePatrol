from sqlalchemy import Column, Integer, String, BigInteger, Numeric, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()

class RawEvent(Base):
    """Stores the raw events emitted by the bridges, before any processing"""
    __tablename__ = 'raw_events'

    id = Column(Integer, primary_key=True)
    chain = Column(String, nullable=False, index=True) # ethereum, polygon
    bridge_name = Column(String, nullable=False, index=True) # polygon_pos, ronin
    event_type = Column(String, nullable=False) # LOCK, MINT, TRANSFER
    
    tx_hash = Column(String, nullable=False, index=True)
    block_number = Column(BigInteger, nullable=False)
    emitter_address = Column(String, nullable=False) # Contrato que emitiu
    
    # Dados brutos do evento (ex: deposit_id, sender, recipient, amount)
    # Aqui podes meter tudo o que é específico de cada bridge
    data = Column(JSONB, nullable=False)
    
    timestamp = Column(DateTime, server_default=func.now())

class CrossChainTx(Base):
    """Main table that represents cross chain transactions"""
    __tablename__ = 'cross_chain_transactions'

    # O Identificador Único da transação cross-chain (ex: deposit_id ou msg_hash)
    cctx_id = Column(String, primary_key=True, index=True)
    bridge_name = Column(String, nullable=False, index=True)

    # Lado da Origem (Source)
    src_chain = Column(String)
    src_tx_hash = Column(String, index=True)
    src_amount = Column(Numeric(78, 0)) # Suporta uint256 sem perder precisão
    src_sender = Column(String)
    src_timestamp = Column(DateTime)
    src_block = Column(BigInteger)

    # Lado do Destino (Destination)
    dst_chain = Column(String)
    dst_tx_hash = Column(String, index=True)
    dst_amount = Column(Numeric(78, 0))
    dst_recipient = Column(String)
    dst_timestamp = Column(DateTime)
    dst_block = Column(BigInteger)

    # Estado: PENDING, COMPLETED, ALERT
    status = Column(String, default='PENDING', index=True)
    
    # Campo para extras específicos (ex: assinaturas de validadores, fees, etc.)
    metadata = Column(JSONB, default={})

class BridgeAlert(Base):
    """Onde as tuas assinaturas (.yml) escrevem os alertas."""
    __tablename__ = 'bridge_alerts'

    id = Column(Integer, primary_key=True)
    signature_id = Column(String, nullable=False, index=True) # ex: OVER_MINT
    severity = Column(String, nullable=False) # LOW, MEDIUM, HIGH, CRITICAL
    
    # Ligação opcional a uma CCTX específica
    cctx_id = Column(String, ForeignKey('cross_chain_transactions.cctx_id'), nullable=True)
    
    # Provas do ataque (os campos definidos no 'evidence' do teu YML)
    evidence = Column(JSONB, nullable=False)
    
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())