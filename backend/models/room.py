from typing import Set, Optional
from pydantic import BaseModel

class VideoSearch(BaseModel):
    query: str
    api_key: str
    
    class Config:
        from_attributes = True

class Room:
    def __init__(self):
        self.users: Set[str] = set()
        self.leader: Optional[str] = None
        self.current_video: Optional[str] = None
        self.video_state: str = 'paused'
        self.current_time: float = 0

    def to_dict(self):
        return {
            'users': list(self.users),
            'leader': self.leader,
            'current_video': self.current_video,
            'video_state': self.video_state,
            'current_time': self.current_time
        }