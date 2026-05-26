from __future__ import annotations

from src.collectors.facebook_live_collector import FacebookLiveCollector
from src.collectors.facebook_collector import FacebookCollector
from src.models import JobPost


def collect_with_fallback(config_path: str) -> list[JobPost]:
    try:
        return FacebookLiveCollector(config_path).collect()
    except Exception:
        return FacebookCollector(config_path).collect()
