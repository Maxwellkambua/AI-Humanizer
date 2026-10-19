from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from .config import settings
from .pipeline.orchestrator import humanize
from .schemas import HumanizeRequest, HumanizeResponse

app = FastAPI(title="AI Humanizer", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND = Path(__file__).resolve().parent.parent / "frontend" / "index.html"


@app.get("/")
async def index():
    return FileResponse(FRONTEND)


@app.get("/health")
async def health():
    return {"status": "ok", "provider": settings.DEFAULT_PROVIDER}


@app.post("/humanize", response_model=HumanizeResponse)
async def humanize_endpoint(req: HumanizeRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="text is empty")
    try:
        return await humanize(req)
    except Exception as e:  # surface provider errors to the client
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {e}")