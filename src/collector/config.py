import yaml
from typing import Dict
from .models import ChainCfg

def load_yaml(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def build_chain_cfgs(chains_doc: dict) -> Dict[str, ChainCfg]:
    chain_cfgs: Dict[str, ChainCfg] = {}

    for name, c in chains_doc["chains"].items():
        rpc_url_list = c.get("rpc_url_list")
        if not rpc_url_list:
            raise RuntimeError(f"Missing 'rpc_url_list' for chain '{name}'")

        chain_cfgs[name] = ChainCfg(
            name=name,
            chain_id=int(c["chain_id"]),
            rpc_url_list=list(rpc_url_list),
            confirmations=int(c.get("confirmations", 0)),
        )

    return chain_cfgs