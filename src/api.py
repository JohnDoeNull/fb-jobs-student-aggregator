from __future__ import annotations

from pathlib import Path
from typing import Optional
from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from src.models import JobPost
from src.pipeline.storage import load_json

DATA_JSON = Path("data/processed/jobs.json")
DATA_CSV = Path("data/processed/jobs.csv")

app = FastAPI(title="FB Jobs Aggregator API", version="0.1.0")
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")


def _read() -> list[JobPost]:
    return load_json(DATA_JSON)


@app.get("/")
def home():
    return RedirectResponse(url="/frontend/index.html")


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/jobs")
def list_jobs(
    q: Optional[str] = None,
    tag: Optional[str] = None,
    location: Optional[str] = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=200),
):
    jobs = _read()

    def ok(item: JobPost) -> bool:
        text = f"{item.title}\n{item.description}".lower()
        if q and q.lower() not in text:
            return False
        if tag and tag.lower() not in [t.lower() for t in item.tags]:
            return False
        if location and location.lower() not in item.location.lower():
            return False
        return True

    filtered = [j for j in jobs if ok(j)]
    total = len(filtered)
    page = filtered[skip : skip + limit]
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": [j.model_dump() for j in page],
    }


@app.get("/export/json")
def export_json():
    return FileResponse(DATA_JSON)


@app.get("/export/csv")
def export_csv():
    return FileResponse(DATA_CSV)
