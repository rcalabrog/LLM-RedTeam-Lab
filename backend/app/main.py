from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.attacks import router as attacks_router
from .api.defenses import router as defenses_router
from .api.evaluation import router as evaluation_router
from .api.health import router as health_router
from .api.llm import router as llm_router
from .api.runs import router as runs_router
from .api.storage import router as storage_router
from .api.targets import router as targets_router
from .api.workflows import router as workflows_router
from .core.config import get_settings
from .core.logging import setup_logging
from .storage import initialize_database

settings = get_settings()
setup_logging(settings.log_level)

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _initialize_storage() -> None:
    initialize_database(settings.sqlite_db_path)


app.include_router(health_router)
app.include_router(health_router, prefix=settings.api_prefix)
app.include_router(attacks_router)
app.include_router(attacks_router, prefix=settings.api_prefix)
app.include_router(defenses_router)
app.include_router(defenses_router, prefix=settings.api_prefix)
app.include_router(evaluation_router)
app.include_router(evaluation_router, prefix=settings.api_prefix)
app.include_router(llm_router)
app.include_router(llm_router, prefix=settings.api_prefix)
app.include_router(runs_router)
app.include_router(runs_router, prefix=settings.api_prefix)
app.include_router(storage_router)
app.include_router(storage_router, prefix=settings.api_prefix)
app.include_router(targets_router)
app.include_router(targets_router, prefix=settings.api_prefix)
app.include_router(workflows_router)
app.include_router(workflows_router, prefix=settings.api_prefix)
