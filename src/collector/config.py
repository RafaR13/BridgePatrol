import os
import yaml
from typing import Dict
from .models import ChainCfg

def load_yaml(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def build_chain_cfgs(chains_doc: dict) -> Dict[str, ChainCfg]:
    chain_cfgs = {}

    for name, c in chains_doc["chains"].items():
        rpc_env = c["rpc_url_env"]
        rpc_url = os.environ.get(rpc_env)
        if not rpc_url:
            raise RuntimeError(f"Missing env var {rpc_env} for chain '{name}'")

        chain_cfgs[name] = ChainCfg(
            name=name,
            chain_id=int(c["chain_id"]),
            rpc_url=rpc_url,
            confirmations=int(c.get("confirmations", 0)),
        )

    return chain_cfgs