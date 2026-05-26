from __future__ import annotations

import json
from pathlib import Path
from typing import List
import yaml
from src.models import JobPost


class FacebookCollector:
    """
    Collector skeleton:
    - Hiện tại: đọc mock JSON để dev nhanh.
    - Mở rộng: dùng Playwright login/session + scrape post công khai.
    """

    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        self.config = yaml.safe_load(self.config_path.read_text(encoding="utf-8"))

    def collect(self) -> List[JobPost]:
        mock_file = Path(__file__).with_name("mock_data.json")
        data = json.loads(mock_file.read_text(encoding="utf-8"))
        return [JobPost(**row) for row in data]
