from typing import List

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

    @property
    def fastapi_kwargs(self):
        return {
            "debug": self.DEBUG,
            "docs_url": "/docs",
            "redoc_url": "/redoc",
        }

settings = Settings()