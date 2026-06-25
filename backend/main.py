import os
import sys
import sqlite3
import traceback

# Make the backend package directory importable by top-level module name, so the
# app works whether launched as "backend.main:app" (from the repo root, as
# run.bat does) or as "main:app" (from within the backend/ directory).
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import database
from routers import rules, audits

# Allowed browser origins for CORS. Restricted to the local dev frontend instead
# of "*"; "*" combined with allow_credentials=True is rejected by browsers and is
# unsafe. Override via the ALLOWED_ORIGINS env var (comma-separated) in prod.
ALLOWED_ORIGINS = [
    o.strip()
    for o in os.environ.get(
        "ALLOWED_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    if o.strip()
]

app = FastAPI(title="LexAudit Backend API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    database.init_db()


# Centralized error handling — route handlers stay free of repetitive try/except.
@app.exception_handler(sqlite3.IntegrityError)
async def integrity_error_handler(request, exc):
    # e.g. creating a rule whose title duplicates an existing one.
    return JSONResponse(status_code=400, content={"detail": f"Database constraint error: {exc}"})


@app.exception_handler(Exception)
async def unhandled_error_handler(request, exc):
    traceback.print_exc()
    return JSONResponse(status_code=500, content={"detail": str(exc)})


app.include_router(rules.router)
app.include_router(audits.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
