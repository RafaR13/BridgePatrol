# storage.py
import json
from hexbytes import HexBytes

def _json_default(o):
    if isinstance(o, HexBytes):
        return o.hex()
    if isinstance(o, (bytes, bytearray)):
        return "0x" + o.hex()
    return str(o)  # fallback seguro (evita crash em tipos estranhos)

def append_jsonl(path: str, obj: dict):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False, default=_json_default) + "\n")