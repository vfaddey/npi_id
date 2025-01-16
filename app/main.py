from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.oidc import router as oidc_router
from app.core.config import settings

app = FastAPI(
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    root_path="/",
    title=settings.APP_NAME
)
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(oidc_router)


app.add_middleware(
    CORSMiddleware,
    allow_origin_regex="https?://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)