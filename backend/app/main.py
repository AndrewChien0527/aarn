from fastapi import FastAPI
from .logging import logger
from .db.base import init_db
from .api.search import router as search_router
from .api.papers import router as papers_router
from .api.admin import router as admin_router
from .config import APP_NAME
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title=APP_NAME)


app.add_middleware(
CORSMiddleware,
allow_origins=["*"],
allow_credentials=True,
allow_methods=["*"],
allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    logger.info("Starting AARN backend")
    init_db()


app.include_router(search_router)
app.include_router(papers_router)
app.include_router(admin_router)


@app.get("/health")
def health():
    return {"status":"ok"}