from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from ..services.user_service import UserService
from ..config.database import get_db
from ..models.schemas import UserCreate, UserLogin, Token
from datetime import datetime, timedelta
from ..config.settings import settings
import jwt
from pydantic import BaseModel

router = APIRouter()

# Request models
class UserRegister(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

@router.post("/register")
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    try:
        user_service = UserService(db)
        new_user = user_service.create_user(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password
        )
        return {"status": "success", "message": "Registration successful"}
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

@router.post("/login", response_model=Token)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    try:
        user_service = UserService(db)
        user = user_service.authenticate_user(
            username=user_data.username,
            password=user_data.password
        )
        
        # Generate access token
        access_token = create_access_token(
            data={"sub": user.username}
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.get("/me")
async def get_user_me(db: Session = Depends(get_db), token: str = Depends(OAuth2PasswordBearer(tokenUrl="login"))):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
            
        user_service = UserService(db)
        user = user_service.get_user_by_username(username)
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
            
        return {
            "username": user.username,
            "email": user.email
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Could not validate token")

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("auth_token")
    return {"message": "Successfully logged out"}