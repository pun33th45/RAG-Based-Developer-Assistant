import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routes import query, upload


settings = get_settings()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s - %(message)s")
logger = logging.getLogger("devinsight")

app = FastAPI(title=settings.app_name, version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router)
app.include_router(query.router)


@app.get("/health")
async def health_check():
    runtime_issues = settings.validate_runtime()
    return {
        "status": "ok" if not runtime_issues else "degraded",
        "service": settings.app_name,
        "llm_configured": settings.is_llm_configured,
        "runtime_issues": runtime_issues,
    }
