from fastapi import FastAPI
from pathlib import Path
from fastapi.responses import FileResponse


app = FastAPI()

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"


@app.get("/")
def home():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/jobs")
def list_jobs():
    return [
        {"id": 1, "title": "Python Developer", "city": "Berlin"},
        {"id": 2, "title": "Kubernetes Administrator", "city": "Bremen"},
    ]
