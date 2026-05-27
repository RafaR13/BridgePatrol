# blockchain-ids-tese

## primeiras bridges a testar
- polygon

```sh
python3 -m venv venv    # in project root
source venv/bin/activate
pip install -r requirements.txt
[deactivate]
```

## Run tests
```sh
python3 -m pytest [tests/TEST_NAME.py]
```

## Run the program

Run commands from the `blockchain-ids-tese` directory:

```sh
cd blockchain-ids-tese
```

### Signature detection only

Runs the analysers over everything already present in the database tables:

```sh
python3 cli.py --bridge ronin --blockchains ethereum ronin
```

Store generated alerts:

```sh
python3 cli.py --bridge ronin --blockchains ethereum ronin --store-alerts
```

Polygon example:

```sh
python3 cli.py --bridge polygon --blockchains ethereum polygon
```

### Normalize then analyse

Use this when raw bridge tables already exist, but normalized events need to be rebuilt:

```sh
python3 cli.py --bridge ronin --blockchains ethereum ronin --need-normalization
```

### Extract, generate, normalize, and analyse

Use this when data still needs to be fetched from `XChainDataGen`. Timestamps are required only for extraction:

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

## [Helper] Clear tables
```sh
python3 -m helpers.clear_tables --table cctp_deposit_for_burn

python3 -m helpers.clear_tables --bridge cctp

python3 -m helpers.clear_tablesy --all
```
### options
- --yes (doesn't ask for confirmation)
- --dry-run (shows what would be erased but doesn't execute)


## Important links
- check topic0's of functions: [openchain.xyz](https://openchain.xyz/)
- scan ethereum activity: [etherscan.io](https://etherscan.io/)
- scan polygon activity: [polygonscan.com](https://polygonscan.com/)
- search for bridges: https://defillama.com/bridges
