from fastapi import APIRouter, HTTPException
import httpx
from ..models.room import VideoSearch

router = APIRouter()

@router.post("/search-youtube")
async def search_youtube(search: VideoSearch):
    async with httpx.AsyncClient() as client:
        try:
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
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))