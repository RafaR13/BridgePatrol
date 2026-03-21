from collections import defaultdict

from db.repository.normalized_event.normalized_event_model import NormalizedEvent
from .types import ALLOWED_SOURCE_DESTINATION_PAIRS

def group_events_by_correlation(events: list[NormalizedEvent]) -> dict[tuple[str, str, str], dict[str, list[NormalizedEvent]]]:
    grouped = defaultdict(lambda: {"sources": [], "destinations": [], "others": []})

    for event in events:
        if event.event_type in ALLOWED_SOURCE_DESTINATION_PAIRS.get(event.bridge, dict()).values() and event.correlation_id:
            key = (event.bridge, event.correlation_type, event.correlation_id)
            if event.event_type == ALLOWED_SOURCE_DESTINATION_PAIRS.get(event.bridge, dict()).get("source"):
                grouped[key]["sources"].append(event)
            elif event.event_type == ALLOWED_SOURCE_DESTINATION_PAIRS.get(event.bridge, dict()).get("dest"):
                grouped[key]["destinations"].append(event)
        else:
            key = (event.bridge, None, None)
            grouped[key]["others"].append(event)
    return dict(grouped)