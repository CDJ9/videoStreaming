import socketio
import logging
from ..models.room import Room

logger = logging.getLogger(__name__)

sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins=["http://localhost:8000", "http://localhost:8080", "http://127.0.0.1:8000", "http://127.0.0.1:8080"],
    logger=True,
    engineio_logger=True,
    ping_timeout=60,
    ping_interval=25
)

rooms = {}

@sio.event
async def connect(sid, environ):
    logger.info(f"Client connected: {sid}")
    await sio.emit('connect_response', {'status': 'connected', 'sid': sid}, room=sid)

@sio.event
async def join_room(sid, data):
    try:
        room_id = data['roomId']
        logger.info(f"User {sid} joining room {room_id}")
        
        if room_id not in rooms:
            rooms[room_id] = {
                'users': set(),
                'leader': sid,
                'current_video': None,
                'video_state': 'paused',
                'current_time': 0
            }
        
        rooms[room_id]['users'].add(sid)
        await sio.enter_room(sid, room_id)
        
        # Send room state to new user
        await sio.emit('room_state', {
            'current_video': rooms[room_id]['current_video'],
            'video_state': rooms[room_id]['video_state'],
            'current_time': rooms[room_id]['current_time'],
            'leader': rooms[room_id]['leader']
        }, room=sid)
        
        # Notify others
        await sio.emit('user_joined', {
            'userId': sid,
            'totalUsers': len(rooms[room_id]['users'])
        }, room=room_id, skip_sid=sid)
        
    except Exception as e:
        logger.error(f"Error in join_room: {e}")
        await sio.emit('error', {'message': str(e)}, room=sid)

@sio.event
async def video_state_change(sid, data):
    try:
        room_id = data['roomId']
        if room_id in rooms:
            # Update room state
            rooms[room_id]['video_state'] = data['state']
            rooms[room_id]['current_time'] = data['currentTime']
            
            # Broadcast to all other users in the room
            await sio.emit('video_state_updated', {
                'state': data['state'],
                'currentTime': data['currentTime'],
                'timestamp': data.get('timestamp'),
                'playbackRate': data.get('playbackRate', 1)
            }, room=room_id, skip_sid=sid)
            
            logger.info(f"Video state changed in room {room_id}: {data['state']} at {data['currentTime']}")
    except Exception as e:
        logger.error(f"Error in video_state_change: {e}")

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
            
            # Broadcast to all users in the room, including sender
            await sio.emit('video_changed', {
                'videoId': video_id,
                'state': 'paused',
                'currentTime': 0
            }, room=room_id)
    except Exception as e:
        logger.error(f"Error in change_video: {e}")

@sio.event
async def video_buffering(sid, data):
    try:
        room_id = data['roomId']
        if room_id in rooms:
            await sio.emit('video_buffering', {
                'state': data['state'],
                'currentTime': data['currentTime']
            }, room=room_id, skip_sid=sid)
    except Exception as e:
        logger.error(f"Error in video_buffering: {e}")

@sio.event
async def disconnect(sid):
    logger.info(f"Client disconnected: {sid}")
    for room_id in list(rooms.keys()):
        if room_id in rooms and 'users' in rooms[room_id] and sid in rooms[room_id]['users']:
            rooms[room_id]['users'].remove(sid)
            if len(rooms[room_id]['users']) == 0:
                del rooms[room_id]
            else:
                # If leader disconnected, assign new leader
                if rooms[room_id]['leader'] == sid:
                    new_leader = next(iter(rooms[room_id]['users']))
                    rooms[room_id]['leader'] = new_leader
                    await sio.emit('leader_changed', {
                        'newLeader': new_leader
                    }, room=room_id)
                await sio.emit('user_left', {
                    'userId': sid,
                    'totalUsers': len(rooms[room_id]['users'])
                }, room=room_id)