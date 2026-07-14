from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.core.database import init_db
from app.core.config import settings
from app.modules.auths.auth_router import router as auth_router
from app.modules.memories.memory_router import router as memory_router
from app.modules.users.user_router import router as user_router
from app.modules.stats.stat_router import router as stat_router
from app.modules.health.health_router import router as health_router
from app.core.logger import logger


# Lifespan function to run startup/shutdown code
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    logger.info("JodJam API started")
    logger.info(
        f"Running in {settings.ENV}"
    )
    yield
    logger.info("JodJam API shutdown")

app = FastAPI(
    title="JodJam API",
    description="Backend API for JodJam",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# MIDDLEWARE
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if settings.ENV == "production":
    app.add_middleware(
        HTTPSRedirectMiddleware
    )

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=[
        "localhost",
        "127.0.0.1",
        "*.onrender.com",
        "*.vercel.app",
    ]
)

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.JWT_SECRET,
    same_site="none",
    https_only=True
)



# ROUTERS
api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router)
api_router.include_router(memory_router)
api_router.include_router(user_router) 
api_router.include_router(stat_router)
api_router.include_router(health_router)

app.include_router(api_router)


# ROOT
@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")

