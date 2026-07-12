import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes import auth, contact, dashboard, analytics, upload
from app.api.routes.content_modules import build_module_router
from app.core.config import get_settings
from app.db.session import Base, SessionLocal, engine
from app.seed import seed_database


settings = get_settings()


def create_app() -> FastAPI:
    is_prod = settings.environment.lower() == "production"
    app = FastAPI(
        title=settings.app_name,
        docs_url=None if is_prod else "/docs",
        redoc_url=None if is_prod else "/redoc",
        openapi_url=None if is_prod else "/openapi.json",
    )
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    def startup() -> None:
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        try:
            seed_database(db)
        finally:
            db.close()

    @app.get("/health")
    def health():
        return {"status": "ok"}

    app.include_router(auth.router, prefix=settings.api_prefix)
    app.include_router(dashboard.router, prefix=settings.api_prefix)
    app.include_router(analytics.router, prefix=settings.api_prefix)
    app.include_router(contact.router, prefix=settings.api_prefix)
    app.include_router(upload.router, prefix=settings.api_prefix)
    for module in ["projects", "blog", "articles", "gallery", "experience", "skills", "profile"]:
        app.include_router(build_module_router(module), prefix=settings.api_prefix)

    return app


app = create_app()
