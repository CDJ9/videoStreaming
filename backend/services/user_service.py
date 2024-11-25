from sqlalchemy.orm import Session
from ..models.user import User  # Updated import
from fastapi import HTTPException
import bcrypt

class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_username(self, username: str) -> User:
        return self.db.query(User).filter(User.username == username).first()

    def get_user_by_email(self, email: str) -> User:
        return self.db.query(User).filter(User.email == email).first()

    def create_user(self, username: str, email: str, password: str) -> User:
        # Check if username or email already exists
        if self.get_user_by_username(username):
            raise HTTPException(status_code=400, detail="Username already registered")
        if self.get_user_by_email(email):
            raise HTTPException(status_code=400, detail="Email already registered")

        # Hash password
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

        # Create user
        user = User(
            username=username,
            email=email,
            hashed_password=hashed_password.decode('utf-8')
        )

        try:
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=400, detail=str(e))

def authenticate_user(self, username: str, password: str) -> User:
    user = self.get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    # Verify password
    try:
        is_valid = bcrypt.checkpw(
            password.encode('utf-8'),
            user.hashed_password.encode('utf-8')
        )
        if not is_valid:
            raise HTTPException(status_code=401, detail="Invalid username or password")
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    return user