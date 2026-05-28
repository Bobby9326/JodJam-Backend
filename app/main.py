from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware


from app.core.database import init_db
from app.core.config import settings
from app.modules.auths.auth_router import router as auth_router
from app.modules.memories.memory_router import router as memory_router
from app.modules.users.user_router import router as user_router
from app.modules.stats.stat_router import router as stat_router



# LOAD ENV



# FASTAPI
app = FastAPI(
    title="My API",
    version="1.0.0",
)


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.JWT_SECRET,
)


# ROUTERS
api_router = APIRouter(prefix="/api")

api_router.include_router(auth_router)
api_router.include_router(memory_router)
api_router.include_router(user_router) 
api_router.include_router(stat_router)

app.include_router(api_router)


# STARTUP
@app.on_event("startup")
async def startup_event():
    init_db()
    print("APP STARTED")


# ROOT
@app.get("/")
async def root():
    return RedirectResponse(url="/docs")