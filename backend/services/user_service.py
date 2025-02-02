from sqlalchemy.orm import Session
from sqlalchemy import text
from ..models.user import User
from fastapi import HTTPException
import bcrypt
import logging

class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_username(self, username: str) -> User:
        try:
            print("\n=== Database Query Debug ===")
            print(f"Looking for username: {username}")
            
            # Execute raw SQL query with proper text() wrapper
            raw_result = self.db.execute(
                text("SELECT * FROM users WHERE username = :username"),
                {"username": username}
            ).fetchone()
            
            if raw_result:
                print("\nRaw SQL result:")
                print(f"  ID: {raw_result[0]}")
                print(f"  Username: {raw_result[1]}")
                print(f"  Password: {raw_result[2]}")
                print(f"  Email: {raw_result[3]}")
            else:
                print("No results found in raw SQL query")

            # Print all users in database for verification
            print("\nAll users in database:")
            all_users = self.db.execute(text("SELECT username, email FROM users")).fetchall()
            for user in all_users:
                print(f"  - Username: {user[0]}, Email: {user[1]}")

            # Try SQLAlchemy ORM query
            query = self.db.query(User).filter(User.username == username)
            print(f"\nSQLAlchemy Query: {str(query)}")
            
            result = query.first()
            if result:
                print("\nFound user via SQLAlchemy:")
                print(f"  ID: {result.id}")
                print(f"  Username: {result.username}")
                print(f"  Password hash: {result.password}")
                print(f"  Email: {result.email}")
            else:
                print("\nNo user found via SQLAlchemy query")

            return result

        except Exception as e:
            print(f"\nError in get_user_by_username: {str(e)}")
            import traceback
            print(f"Traceback:\n{traceback.format_exc()}")
            raise

    def authenticate_user(self, username: str, password: str) -> User:
        print("\n=== Authentication Debug ===")
        print(f"Login attempt for username: {username}")
        
        user = self.get_user_by_username(username)
        
        if not user:
            print(f"User not found: {username}")
            raise HTTPException(status_code=401, detail="Incorrect username or password")

        try:
            print("\nAttempting password verification:")
            print(f"Stored hash: {user.password}")
            print(f"Provided password: {password}")
            
            # Verify password
            stored_password = user.password.encode('utf-8')
            provided_password = password.encode('utf-8')
            
            print(f"\nEncoded values:")
            print(f"Stored: {stored_password}")
            print(f"Provided: {provided_password}")
            
            result = bcrypt.checkpw(provided_password, stored_password)
            print(f"Password verification result: {result}")
            
            if not result:
                print("Password verification failed")
                raise HTTPException(status_code=401, detail="Incorrect username or password")
            
            print("Authentication successful!")
            return user
            
        except Exception as e:
            print(f"\nError during password verification: {str(e)}")
            import traceback
            print(f"Traceback:\n{traceback.format_exc()}")
            raise HTTPException(status_code=401, detail="Authentication error")