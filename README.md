# blockchain-ids-tese

## primeiras bridges a testar
- polygon

```sh
python3 -m venv venv    # in project root
source venv/bin/activate
[deactivate]
```

## Run tests
```sh
python3 -m pytest [tests/TEST_NAME.py]
```

## Correr colector

```sh
python3 -m __init__ [realtime/forensic] --bridge [bridge name] --chains [chain1, chain2, ...] --last-n-blocks [n]
```


## Important links
- check topic0's of functions: [openchain.xyz](https://openchain.xyz/)
- scan ethereum activity: [etherscan.io](https://etherscan.io/)
- scan polygon activity: [polygonscan.com](https://polygonscan.com/)
- search for bridges: https://defillama.com/bridges