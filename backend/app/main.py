from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database.session import init_db
from app.api.events import router as events_router
from app.api.sessions import router as sessions_router
from app.api.automata import router as automata_router
from app.api.simulator import router as simulator_router
from app.api.experiments import router as experiments_router
from app.api.websocket import router as ws_router
from app.services.seed import seed_demo_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await seed_demo_data()
    yield


app = FastAPI(
    title="Digital Doppelganger",
    description="Automata-based behavioral intelligence platform",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(events_router, prefix="/api/events", tags=["events"])
app.include_router(sessions_router, prefix="/api/sessions", tags=["sessions"])
app.include_router(automata_router, prefix="/api/automata", tags=["automata"])
app.include_router(simulator_router, prefix="/api/simulator", tags=["simulator"])
app.include_router(experiments_router, prefix="/api/experiments", tags=["experiments"])
app.include_router(ws_router, prefix="/ws", tags=["websocket"])


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "digital-doppelganger"}
