from sqlalchemy.orm import Session
from ..models.user import User
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

class UserService:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, username: str, email: str, password: str) -> User:
        try:
            user = User(
                username=username,
                email=email,
                hashed_password=User.hash_password(password)
            )
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=400,
                detail="Username or email already exists"
            )

    def get_user_by_username(self, username: str) -> User:
        return self.db.query(User).filter(User.username == username).first()

    def get_user_by_email(self, email: str) -> User:
        return self.db.query(User).filter(User.email == email).first()

    def authenticate_user(self, username: str, password: str) -> User:
        user = self.get_user_by_username(username)
        if not user or not user.verify_password(password):
            raise HTTPException(
                status_code=401,
                detail="Incorrect username or password"
            )
        return user