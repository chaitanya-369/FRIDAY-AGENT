from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from friday.api.routes import chat
from friday.api.routes.providers import router as providers_router
from friday.api.routes.keys import router as keys_router
from friday.api.routes.models_catalog import router as models_router
from friday.api.routes.session import router as session_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown lifecycle — launches the Slack bot alongside the API."""
    # ── Startup ──────────────────────────────────────────────────────────────
    try:
        from friday.interfaces.slack_bot import start_in_background

        start_in_background()
    except Exception as e:
        # Never let a Slack config error crash the whole API server
        print(f"[FRIDAY Slack] Could not start Slack bot: {e}")

    yield  # API is now serving requests

    # ── Shutdown (daemon thread dies with the process automatically) ─────────
    print("[FRIDAY] Shutting down...")


app = FastAPI(
    title="FRIDAY Agent Gateway",
    description="API for the Female Replacement Intelligent Digital Assistant Youth",
    version="1.0.0",
    lifespan=lifespan,
)

# Allow CORS for HUD/Mobile
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(providers_router)
app.include_router(keys_router)
app.include_router(models_router)
app.include_router(session_router)


@app.get("/status")
def status():
    return {"status": "nominal", "message": "All systems operational, Boss."}
