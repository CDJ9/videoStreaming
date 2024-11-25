from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from .api.routes import router as socket_router
from .api.auth_routes import router as auth_router  # Change from user_routes to auth_routes
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

# Mount routes - note the order is important
app.include_router(auth_router, prefix="/api/users", tags=["authentication"])  # Auth routes first
app.include_router(socket_router)  # Socket routes second

# Socket.IO setup
socket_app = socketio.ASGIApp(sio)
app.mount("/socket.io", socket_app)

# Serve static files
app.mount("/static", StaticFiles(directory=str(ROOT_DIR / "frontend" / "static")), name="static")

# Serve auth page - this needs to come before the catch-all route
@app.get("/auth")
async def auth_page():
    return FileResponse(str(ROOT_DIR / "frontend" / "static" / "auth.html"))

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Root route to serve index.html
@app.get("/")
async def read_root():
    return FileResponse(str(ROOT_DIR / "frontend" / "static" / "index.html"))

# Catch-all route for other paths - this should be last
@app.get("/{full_path:path}")
async def catch_all(full_path: str):
    # First check if the path exists in static
    static_path = ROOT_DIR / "frontend" / "static" / full_path
    if static_path.exists() and static_path.is_file():
        return FileResponse(str(static_path))
    # If not found, return index.html for client-side routing
    return FileResponse(str(ROOT_DIR / "frontend" / "static" / "index.html"))