from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable
import pandas as pd
from src.models import JobPost


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def save_json(path: Path, jobs: Iterable[JobPost]) -> None:
    ensure_parent(path)
    rows = [j.model_dump() for j in jobs]
    path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")


def save_csv(path: Path, jobs: Iterable[JobPost]) -> None:
    ensure_parent(path)
    rows = [j.model_dump() for j in jobs]
    df = pd.DataFrame(rows)
    if "tags" in df.columns:
        df["tags"] = df["tags"].apply(lambda x: ",".join(x) if isinstance(x, list) else "")
    df.to_csv(path, index=False)


def load_json(path: Path) -> list[JobPost]:
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return [JobPost(**item) for item in data]
