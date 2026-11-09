import os

import psycopg
from psycopg.rows import dict_row
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


#@app.get("/api/jobs")
#def list_jobs():
#    return [
#        {"id": 1, "title": "Python Developer", "city": "Berlin"},
#        {"id": 2, "title": "Kubernetes Administrator", "city": "Bremen"},
#    ]

@app.get("/api/jobs")
def list_jobs():
    with psycopg.connect(
        host=os.environ["POSTGRES_HOST"],
        port=os.environ.get("POSTGRES_PORT", "5432"),
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        connect_timeout=5,
        row_factory=dict_row,
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, title, city FROM jobs ORDER BY id"
            )
            return cursor.fetchall()
