# Blockchain IDS Thesis Implementation

> This repository contains the implementation developed for a master's thesis.
>
> TODO: add thesis link when the final document is publicly available.

## Overview

This project implements an intrusion-detection pipeline for cross-chain bridge
activity. It uses bridge-specific blockchain data, normalizes raw protocol events
into a common event model, and runs signature-based checks to detect suspicious
or inconsistent cross-chain behavior.

The implementation is designed to support thesis experimentation around bridge
security, including:

- extraction and generation of bridge datasets through `XChainDataGen`;
- normalization of raw bridge tables into a shared schema;
- signature detection over normalized events and generated cross-chain
  transactions;
- optional persistence of generated alerts;
- correctness and performance evaluation scripts.

## Repository Layout


```text
.
├── cli.py                         # Main pipeline CLI
├── config/                        # Environment and shared constants
├── db/                            # SQLAlchemy database setup and repositories
├── evaluation/                    # Evaluation metrics and report helpers
├── helpers/                       # Operational helper scripts
├── normalization/                 # Bridge-specific normalization mappers
├── signature_detection/           # Signature definitions and analysers
├── tests/                         # Sanity, normalization, detection, evaluation tests
└── requirements.txt               # Python dependencies for this project
```


## Requirements

- Python 3.11 or newer
- PostgreSQL, for any command or test that reads/writes bridge data
- A valid `DATABASE_URL`
- RPC/API configuration for `XChainDataGen` when running extraction

## Setup

Create and activate a virtual environment:

```sh
cd BridgePatrol
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create a local environment file:

```sh
cp .env.template .env
```

Edit `.env` and set:

```text
DATABASE_URL=postgresql://USER:PASSWORD@HOST:PORT/DBNAME
```

Example for the PostgreSQL service defined in XChainDataGen:

```text
DATABASE_URL=postgresql://user:password@localhost:5432/db_app
```

Load the variables into the current shell before running the CLI or tests:

```sh
set -a
source .env
set +a
```

When running extraction through `XChainDataGen`, also configure the RPC and API
environment variables required by that project. See `XChainDataGen/README.md`
and `XChainDataGen/config/copy_rpcs_base_config.yaml`.

## Optional Database Setup With Docker

If you want to reuse the PostgreSQL container from `XChainDataGen`, start it from
the workspace root:

```sh
docker-compose up --build -d db
```

Then use:

```text
DATABASE_URL=postgresql://user:password@localhost:5432/db_app
```

## Running The System

The main CLI can run three phases:

1. extraction and cross-chain transaction generation through `XChainDataGen`;
2. normalization of raw bridge tables;
3. signature detection.

### Signature Detection Only

Use this when the database already contains the required raw/normalized data:

```sh
python3 cli.py --bridge ronin --blockchains ethereum ronin
```

Persist generated alerts:

```sh
python3 cli.py --bridge ronin --blockchains ethereum ronin --store-alerts
```

Polygon example:

```sh
python3 cli.py --bridge polygon --blockchains ethereum polygon
```

### Normalize Then Analyse

Use this when raw bridge tables already exist but normalized events should be
rebuilt before detection:

```sh
python3 cli.py --bridge ronin --blockchains ethereum ronin --need-normalization
```

### Extract, Generate, Normalize, And Analyse

Use this when data still needs to be fetched through `XChainDataGen`. Timestamps
are required only when `--need-extraction` is used:

```sh
python3 cli.py \
  --bridge ronin \
  --blockchains ethereum ronin \
  --start-ts 1735689600 \
  --end-ts 1735776000 \
  --need-extraction \
  --need-normalization
```

Add `--store-alerts` if the detected alerts should be persisted.

### Evaluation Report Output

The CLI can also append timing and summary records to a JSONL evaluation file:

```sh
python3 cli.py \
  --bridge polygon \
  --blockchains ethereum polygon \
  --need-normalization \
  --evaluation-report tests/evaluation/results/evaluation.jsonl \
  --evaluation-run-id local-polygon-run
```

## Testing

Run all tests:

```sh
python3 -m pytest
```

Run a specific test file:

```sh
python3 -m pytest tests/evaluation/test_metrics.py
```

Run one test area:

```sh
python3 -m pytest tests/sanity_checks/normalization
python3 -m pytest tests/sanity_checks/signature_detection
```

Some sanity checks require a reachable database and populated tables. Tests that
only exercise pure metric logic, mappers, or synthetic detection fixtures are
safer to run in a clean local setup.

## Evaluation Scripts

Performance:

```sh
python3 -m tests.evaluation.run_performance \
  --bridge polygon \
  --output tests/evaluation/results/evaluation.jsonl
```

Correctness without labels:

```sh
python3 -m tests.evaluation.evaluate_correctness \
  --bridge polygon \
  --output tests/evaluation/results/evaluation.jsonl
```

Global correctness summary, excluding a bridge:

```sh
python3 -m tests.evaluation.evaluate_correctness \
  --bridge all \
  --exclude-bridge ronin
```

Global performance summary, excluding a bridge:

```sh
python3 -m tests.evaluation.run_performance \
  --bridge all \
  --exclude-bridge ronin
```

Performance can run all phases, only normalization, or only signature detection:

```sh
python3 -m tests.evaluation.run_performance --bridge all --phase all
python3 -m tests.evaluation.run_performance --bridge all --phase normalization
python3 -m tests.evaluation.run_performance --bridge all --phase signature-detection
```

Correctness with labels:

```sh
python3 -m tests.evaluation.evaluate_correctness \
  --bridge polygon \
  --labels tests/evaluation/labels/polygon.csv \
  --output tests/evaluation/results/evaluation.jsonl
```

Label CSV format:

```csv
bridge,signature_type,correlation_id,expected_alert
polygon,LOCK_WITHOUT_MINT,123,true
polygon,RECIPIENT_MISMATCH,456,false
```

Use `expected_alert=true` for ground-truth positives and `false` for
ground-truth negatives. Predictions not present in the label file are counted as
false positives.

## Helper Scripts

Convert a date/time into a Unix timestamp:

```sh
python3 -m helpers.getUnixTimestamp 2025-01-01 --time 00:00:00
```

Clear a specific table:

```sh
python3 -m helpers.clear_tables --table cctp_deposit_for_burn
```

Clear all tables for one bridge:

```sh
python3 -m helpers.clear_tables --bridge cctp
```

Clear all tables:

```sh
python3 -m helpers.clear_tables --all
```

Useful options:

- `--yes`: do not ask for interactive confirmation;
- `--dry-run`: show what would be deleted without deleting anything;
- `--no-restart-identity`: keep table identities/sequences;
- `--no-cascade`: avoid `CASCADE` in the `TRUNCATE`.

## Supported Bridges

The current codebase includes extraction, normalization, detection, or tests for
several bridges, including:

- Across
- CCIP
- CCTP
- ChainSwap
- deBridge
- Mayan
- Meter.io
- Nomad
- OmniBridge
- Polygon
- pNetwork
- Qubit
- Ronin
- Stargate
- THORChain

Support is not identical across all phases. Check the corresponding mapper,
analyser, and test files before assuming a bridge has full extraction,
normalization, detection, and evaluation coverage.

## Useful Links

- Function/topic signatures: https://openchain.xyz/
- Ethereum explorer: https://etherscan.io/
- Polygon explorer: https://polygonscan.com/
- Bridge discovery: https://defillama.com/bridges
