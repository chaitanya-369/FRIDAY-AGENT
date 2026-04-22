from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from friday.api.routes import chat

app = FastAPI(
    title="FRIDAY Agent Gateway",
    description="API for the Female Replacement Intelligent Digital Assistant Youth",
    version="1.0.0",
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


@app.get("/status")
def status():
    return {"status": "nominal", "message": "All systems operational, Boss."}
