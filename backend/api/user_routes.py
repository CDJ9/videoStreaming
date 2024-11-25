from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..services.user_service import UserService
from ..config.database import get_db
from pydantic import BaseModel

router = APIRouter()

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

@router.post("/register")
async def register(user: UserCreate, db: Session = Depends(get_db)):
    user_service = UserService(db)
    try:
        user = user_service.create_user(
            username=user.username,
            email=user.email,
            password=user.password
        )
        return {"message": "User created successfully"}
    except HTTPException as e:
        raise e

@router.post("/login")
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user_service = UserService(db)
    try:
        user = user_service.authenticate_user(
            username=user_data.username,
            password=user_data.password
        )
        return {"message": "Login successful"}
    except HTTPException as e:
        raise e