# blockchain-ids-tese

```sh
python3 -m venv venv    # in project root
source venv/bin/activate
[deactivate]
```

## Correr colector

```sh
cd src
python3 -m collector.main --last-n-blocks [n] [--chunk-size n] --out ../out_test
```