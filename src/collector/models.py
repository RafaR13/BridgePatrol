from dataclasses import dataclass

@dataclass
class ChainCfg:
    name: str
    chain_id: int
    rpc_url: str
    confirmations: int