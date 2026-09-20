import os
from typing import List, Union
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "ZERVO"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "zervo_super_secret_jwt_key_2026_change_in_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30  # 30 days

    # Gemini AI
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"

    # Database
    DATABASE_URL: str = "sqlite:///./zervo.db"
    SUPABASE_DATABASE_URL: str = ""

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
        "*"
    ]

    @property
    def active_database_url(self) -> str:
        url = self.SUPABASE_DATABASE_URL
        if not url or "YOUR-PASSWORD" in url or "[PASSWORD]" in url:
            return self.DATABASE_URL
        
        # Clean potential brackets around password e.g. :[mypassword]@
        import re, urllib.parse
        bracket_match = re.search(r':\[(.*?)\]@', url)
        if bracket_match:
            raw_pass = bracket_match.group(1)
            enc_pass = urllib.parse.quote_plus(raw_pass)
            url = url[:bracket_match.start()] + f":{enc_pass}@" + url[bracket_match.end():]

        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        return url

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
