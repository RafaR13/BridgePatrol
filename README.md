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