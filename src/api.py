from __future__ import annotations

from pathlib import Path
from typing import Optional
from fastapi import FastAPI, Query, WebSocket
from src.main import run_pipeline
from fastapi.responses import FileResponse
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
import asyncio

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

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


@app.post("/refresh")
def refresh(config_path: str = "configs/groups.yaml"):
    run_pipeline(config_path)
    jobs = _read()
    return {"ok": True, "count": len(jobs)}

LOG_FILE = Path.home() / ".hermes/logs/agent.log"

async def tail_logs():
    if not LOG_FILE.exists():
        await manager.broadcast(f"ERROR: Log file not found at {LOG_FILE}")
        return

    proc = await asyncio.create_subprocess_shell(
        f"tail -n 50 -f {LOG_FILE}",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    while proc.stdout and not proc.stdout.at_eof():
        line = await proc.stdout.readline()
        if line:
            await manager.broadcast(line.decode().strip())

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(tail_logs())

@app.websocket("/ws/monitor")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Giữ kết nối mở để client có thể nhận broadcast
            await websocket.receive_text()
    except Exception:
        manager.disconnect(websocket)
