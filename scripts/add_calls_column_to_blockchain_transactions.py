from __future__ import annotations

import sys
from pathlib import Path

from sqlalchemy import text

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from config.env import load_env_file

load_env_file(REPO_ROOT / ".env")

from db.database import engine


BLOCKCHAIN_TRANSACTION_TABLES = (
    "across_blockchain_transactions",
    "ccip_blockchain_transactions",
    "cctp_blockchain_transactions",
    "debridge_blockchain_transactions",
    "mayan_blockchain_transactions",
    "meterio_blockchain_transactions",
    "nomad_blockchain_transactions",
    "omnibridge_blockchain_transactions",
    "polygon_blockchain_transactions",
    "pnetwork_bsc_blockchain_transactions",
    "pnetwork_bitcoin_blockchain_transactions",
    "qubit_blockchain_transactions",
    "ronin_blockchain_transactions",
    "thorchain_blockchain_transactions",
)


def main() -> int:
    with engine.begin() as connection:
        for table in BLOCKCHAIN_TRANSACTION_TABLES:
            connection.execute(
                text(f'ALTER TABLE IF EXISTS "{table}" ADD COLUMN IF NOT EXISTS calls JSON')
            )
            print(f"ensured calls column on {table}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
