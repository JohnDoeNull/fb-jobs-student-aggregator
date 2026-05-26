from __future__ import annotations

import re
from typing import Iterable
from src.models import JobPost


RULES = {
    "student": [r"\bsinh viên\b", r"\bsv\b", r"intern", r"thực tập"],
    "part-time": [r"part[ -]?time", r"thời vụ", r"ca tối", r"xoay ca"],
    "it": [r"developer", r"engineer", r"backend", r"frontend", r"fullstack", r"data", r"devops", r"it\b"],
}


def classify_text(text: str) -> list[str]:
    t = (text or "").lower()
    labels: list[str] = []
    for label, patterns in RULES.items():
        if any(re.search(p, t, flags=re.IGNORECASE) for p in patterns):
            labels.append(label)
    if not labels:
        labels.append("other")
    return sorted(set(labels))


def enrich_jobs(jobs: Iterable[JobPost]) -> list[JobPost]:
    out: list[JobPost] = []
    for j in jobs:
        merged = f"{j.title}\n{j.description}"
        labels = classify_text(merged)
        merged_tags = sorted(set((j.tags or []) + labels))
        out.append(j.model_copy(update={"tags": merged_tags}))
    return out
