from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from .api.routes import router as socket_router
from .api.user_routes import router as user_router
from .api.websocket import sio
from .config.database import engine, Base
import socketio
import os
from pathlib import Path

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get the root directory
ROOT_DIR = Path(__file__).parent.parent

# Mount routes
app.include_router(socket_router)
app.include_router(user_router, prefix="/api/users", tags=["users"])

# Socket.IO setup
socket_app = socketio.ASGIApp(sio)
app.mount("/socket.io", socket_app)

# Serve static files
app.mount("/static", StaticFiles(directory=str(ROOT_DIR / "frontend" / "static")), name="static")

# Root route to serve index.html
@app.get("/")
async def read_root():
    return FileResponse(str(ROOT_DIR / "frontend" / "static" / "index.html"))

# Catch-all route for other paths
@app.get("/{full_path:path}")
async def catch_all(full_path: str):
    static_path = ROOT_DIR / "frontend" / "static" / full_path
    if static_path.exists():
        return FileResponse(str(static_path))
    return FileResponse(str(ROOT_DIR / "frontend" / "static" / "index.html"))