from typing import List
import secrets

class Settings:
    CORS_ORIGINS: List[str] = [
        "http://localhost:8000",
        "http://localhost:8080",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:8080"
    ]
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    VERSION: str = "1.0.0"

        # Database settings
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_NAME: str = "video_sync"
    DB_USER: str = "root"  # Update with your MySQL username
    DB_PASSWORD: str = "Sherlock980!"   # Update with your MySQL password

    # Security settings
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    ALGORITHM: str = "HS256"

    @property
    def fastapi_kwargs(self):
        return {
            "debug": self.DEBUG,
            "docs_url": "/docs",
            "redoc_url": "/redoc",
        }

settings = Settings()