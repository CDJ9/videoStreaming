from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from .config.settings import settings
from .api.routes import router
from .api.websocket import sio
import socketio
import logging

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Socket.IO app
socket_app = socketio.ASGIApp(sio)

# Enable CORS with specific origins
origins = [
    "http://localhost:8000",
    "http://localhost:8080",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8080"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Socket.IO app first
app.mount("/socket.io", socket_app)

# Mount API routes
app.include_router(router)

# Serve static files
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Root route to serve index.html
@app.get("/")
async def read_root():
    return FileResponse("frontend/static/index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info",
        access_log=True,
        workers=1
    )