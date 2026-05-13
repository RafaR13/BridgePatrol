import os

try:
    from web3 import Web3
except ImportError:
    Web3 = None

ROOT_CHAIN_MANAGER = "0xA0c68C638235ee32657e8f720a23ceC1bFc77C77"
ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"

ROOT_CHAIN_MANAGER_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "rootToken", "type": "address"}],
        "name": "rootToChildToken",
        "outputs": [{"name": "", "type": "address"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    }
]


def normalize_address(address: str | None) -> str | None:
    if not address:
        return None
    return str(address).lower()


def get_rpc_url(cli_rpc_url: str | None) -> str:
    if cli_rpc_url:
        return cli_rpc_url

    for env_var in ("ETHEREUM_RPC_URL", "ETH_RPC_URL", "WEB3_PROVIDER_URI"):
        rpc_url = os.getenv(env_var)
        if rpc_url:
            return rpc_url

    raise ValueError(
        "Ethereum RPC URL not found. Set ETHEREUM_RPC_URL or pass --rpc-url."
    )


def get_web3_class():
    if Web3 is None:
        raise ImportError(
            "web3 is required. Install dependencies with: pip install -r requirements.txt"
        )
    return Web3


def get_root_chain_manager_contract(rpc_url: str):
    web3_cls = get_web3_class()
    web3 = web3_cls(web3_cls.HTTPProvider(rpc_url))
    if not web3.is_connected():
        raise ConnectionError("Could not connect to Ethereum RPC.")

    return web3.eth.contract(
        address=web3_cls.to_checksum_address(ROOT_CHAIN_MANAGER),
        abi=ROOT_CHAIN_MANAGER_ABI,
    )


def resolve_child_token(contract, root_token: str) -> str | None:
    web3_cls = get_web3_class()
    checksum_root_token = web3_cls.to_checksum_address(root_token)
    child_token = contract.functions.rootToChildToken(checksum_root_token).call()
    child_token = normalize_address(child_token)

    if child_token == ZERO_ADDRESS:
        return None
    return child_token
