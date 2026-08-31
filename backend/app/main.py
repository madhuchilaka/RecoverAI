from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.transactions import router as transaction_router
from app.api.recovery import router as recovery_router
from app.database import init_db

app = FastAPI(
    title="RecoverAI API",
    description="Demo fintech revenue recovery API for test-mode operations.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event() -> None:
    init_db()


app.include_router(transaction_router)
app.include_router(recovery_router)


@app.get("/health")
def health_check() -> dict:
    return {
        "status": "ok",
        "service": "RecoverAI backend",
        "environment": "demo",
        "synthetic_data": True,
    }
