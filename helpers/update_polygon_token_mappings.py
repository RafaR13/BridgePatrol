import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.env import load_env_file
from helpers.polygon_root_chain_manager import (
    get_root_chain_manager_contract,
    get_rpc_url,
    resolve_child_token,
)


def update_mappings(rpc_url: str, discover_observed: bool = True) -> tuple[int, int]:
    from db.repository.polygon_token_mapping.polygon_token_mapping_repository import (
        PolygonTokenMappingRepository,
    )

    contract = get_root_chain_manager_contract(rpc_url)
    PolygonTokenMappingRepository.ensure_tables()

    inserted = 0
    if discover_observed:
        inserted = PolygonTokenMappingRepository.insert_missing_root_tokens(
            PolygonTokenMappingRepository.get_observed_root_tokens()
        )

    checked_at = datetime.now(timezone.utc)
    updated = 0

    for row in PolygonTokenMappingRepository.get_all_ordered():
        child_token = resolve_child_token(contract, row.root_token)
        PolygonTokenMappingRepository.upsert(row.root_token, child_token, checked_at)
        updated += 1

    return inserted, updated


def main():
    load_env_file(PROJECT_ROOT / ".env")

    parser = argparse.ArgumentParser(
        description="Refresh Polygon root token -> child token mappings."
    )
    parser.add_argument(
        "--rpc-url",
        type=str,
        default=None,
        help=(
            "Ethereum RPC URL. Defaults to ETHEREUM_RPC_URL, ETH_RPC_URL, "
            "or WEB3_PROVIDER_URI."
        ),
    )
    parser.add_argument(
        "--no-discover-observed",
        action="store_true",
        help="Only refresh rows already present in polygon_token_mappings.",
    )

    args = parser.parse_args()
    rpc_url = get_rpc_url(args.rpc_url)

    inserted, updated = update_mappings(
        rpc_url=rpc_url,
        discover_observed=not args.no_discover_observed,
    )

    print(f"Inserted missing root tokens: {inserted}")
    print(f"Updated checked mappings: {updated}")


if __name__ == "__main__":
    main()
