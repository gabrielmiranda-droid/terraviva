from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.core.config import settings
from app.db.seed import seed_initial_data


class StripBackendPrefixMiddleware:
    def __init__(self, app, prefix: str) -> None:
        self.app = app
        self.prefix = prefix.rstrip("/")

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http" and scope.get("path", "").startswith(f"{self.prefix}/"):
            scope = dict(scope)
            scope["root_path"] = f"{scope.get('root_path', '')}{self.prefix}"
            scope["path"] = scope["path"][len(self.prefix) :] or "/"
        await self.app(scope, receive, send)


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.AUTO_SEED:
        seed_initial_data()
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="0.1.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin).rstrip("/") for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(StripBackendPrefixMiddleware, prefix="/_/backend")


@app.get("/health", tags=["system"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(api_router, prefix=settings.API_V1_STR)
