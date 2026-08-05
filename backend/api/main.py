import logging
from typing import Generator

from fastapi import Depends, FastAPI

from backend.config.settings import settings
from backend.api.routes import router
from backend.database.connection import SessionLocal, init_db


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger("investment_ai")


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI(title=settings.app_name, debug=settings.debug)
app.include_router(router, dependencies=[Depends(get_db)])


@app.on_event("startup")
async def on_startup() -> None:
    logger.info("Initializing database schema...")
    init_db()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "app": settings.app_name}
