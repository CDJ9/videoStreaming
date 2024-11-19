from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import socketio
import uvicorn
from typing import Dict
import httpx
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import logging

app = FastAPI()
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins=['http://localhost:8080'],
    logger=True,
    engineio_logger=True
)
socket_app = socketio.ASGIApp(sio)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# Store room information
rooms: Dict[str, Dict] = {}

class VideoSearch(BaseModel):
    query: str
    api_key: str

# Update the rooms dictionary structure


@sio.event
async def join_room(sid, data):
    try:
        room_id = data['roomId']
        logger.info(f"User {sid} joining room {room_id}")
        
        if room_id not in rooms:
            rooms[room_id] = {
                'users': set(),
                'leader': sid,  # First user is leader
                'current_video': None,
                'video_state': 'paused',
                'current_time': 0
            }
        
        rooms[room_id]['users'].add(sid)
        await sio.enter_room(sid, room_id)
        
        # Send room state and leader information
        await sio.emit('room_state', {
            'current_video': rooms[room_id]['current_video'],
            'video_state': rooms[room_id]['video_state'],
            'current_time': rooms[room_id]['current_time'],
            'leader': rooms[room_id]['leader']
        }, room=sid)
        
        await sio.emit('user_joined', {
            'userId': sid,
            'totalUsers': len(rooms[room_id]['users']),
            'leader': rooms[room_id]['leader']
        }, room=room_id, skip_sid=sid)

    except Exception as e:
        logger.error(f"Error in join_room: {e}")
        await sio.emit('error', {'message': str(e)}, room=sid)

@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")
    for room_id in rooms:
        if 'users' in rooms[room_id] and sid in rooms[room_id]['users']:
            rooms[room_id]['users'].remove(sid)
            
            # If leader disconnected, assign new leader
            if rooms[room_id]['leader'] == sid and rooms[room_id]['users']:
                new_leader = next(iter(rooms[room_id]['users']))
                rooms[room_id]['leader'] = new_leader
                await sio.emit('leader_changed', {
                    'newLeader': new_leader
                }, room=room_id)
            
            await sio.emit('user_left', {'userId': sid}, room=room_id)
@app.post("/search-youtube")
async def search_youtube(search: VideoSearch):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://www.googleapis.com/youtube/v3/search",
            params={
                "part": "snippet",
                "maxResults": 10,
                "q": search.query,
                "type": "video",
                "key": search.api_key
            }
        )
        return response.json()

@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")

@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")
    for room_id in rooms:
        if 'users' in rooms[room_id] and sid in rooms[room_id]['users']:
            rooms[room_id]['users'].remove(sid)
            # Notify others in room
            await sio.emit('user_left', {'userId': sid}, room=room_id)

# Update the join_room event
@sio.event
async def join_room(sid, data):
    try:
        room_id = data['roomId']
        logger.info(f"User {sid} joining room {room_id}")
        
        if room_id not in rooms:
            rooms[room_id] = {
                'users': set(),
                'current_video': None,
                'video_state': 'paused',
                'current_time': 0
            }
        
        rooms[room_id]['users'].add(sid)
        await sio.enter_room(sid, room_id)
        
        # Log room state
        logger.info(f"Room {room_id} state: {rooms[room_id]}")
        
        # Send current room state to new user
        await sio.emit('room_state', {
            'current_video': rooms[room_id]['current_video'],
            'video_state': rooms[room_id]['video_state'],
            'current_time': rooms[room_id]['current_time']
        }, room=sid)
        
        # Notify others in room
        await sio.emit('user_joined', {
            'userId': sid,
            'totalUsers': len(rooms[room_id]['users'])
        }, room=room_id, skip_sid=sid)
    except Exception as e:
        logger.error(f"Error in join_room: {e}")
        await sio.emit('error', {'message': str(e)}, room=sid)

@sio.event
async def video_state_change(sid, data):
    room_id = data['roomId']
    if room_id in rooms:
        rooms[room_id]['video_state'] = data['state']
        rooms[room_id]['current_time'] = data['currentTime']
        # Include timestamp in the response
        await sio.emit('video_state_updated', {
            'state': data['state'],
            'currentTime': data['currentTime'],
            'timestamp': data.get('timestamp', None)
        }, room=room_id, skip_sid=sid)

# Update the change_video event
@sio.event
async def change_video(sid, data):
    try:
        room_id = data['roomId']
        video_id = data['videoId']
        logger.info(f"Changing video in room {room_id} to {video_id}")
        
        if room_id in rooms:
            rooms[room_id]['current_video'] = video_id
            rooms[room_id]['current_time'] = 0
            rooms[room_id]['video_state'] = 'paused'
            
            await sio.emit('video_changed', {
                'videoId': video_id
            }, room=room_id)
    except Exception as e:
        logger.error(f"Error in change_video: {e}")
        await sio.emit('error', {'message': str(e)}, room=sid)

@sio.event
async def webrtc_signal(sid, data):
    target_sid = data['target']
    await sio.emit('webrtc_signal', {
        'signal': data['signal'],
        'from': sid
    }, room=target_sid)

    
# Add error handling middleware
@app.middleware("http")
async def add_error_handling(request, call_next):
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        logger.error(f"Error handling request: {e}")
        return JSONResponse(
            status_code=500,
            content={"message": str(e)}
        )
@sio.event
async def video_buffering(sid, data):
    room_id = data['roomId']
    if room_id in rooms:
        rooms[room_id]['video_state'] = 'buffering'
        rooms[room_id]['current_time'] = data['currentTime']
        await sio.emit('video_buffering', {
            'state': data['state'],
            'currentTime': data['currentTime']
        }, room=room_id, skip_sid=sid)
app.mount('/', socket_app)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
