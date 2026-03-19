import json
from decimal import Decimal


def to_str(value):
    if value is None:
        return None
    return str(value)


def to_json(data: dict) -> str:
    def serializer(obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return str(obj)

    return json.dumps(data, default=serializer, ensure_ascii=False)