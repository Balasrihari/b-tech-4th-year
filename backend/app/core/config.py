from pydantic_settings import BaseSettings
from typing import Optional, List
import secrets
import os


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "AI-Powered Smart Student Learning Assistant"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    LOG_DIR: str = "logs"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database
    DATABASE_URL: str = "sqlite:///./student_learning.db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # JWT - Use strong secret key in production
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # AI
    GEMINI_API_KEY: Optional[str] = None
    
    # Security
    SECURE_HEADERS: bool = True
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 100
    
    # Password requirements
    MIN_PASSWORD_LENGTH: int = 8
    REQUIRE_PASSWORD_UPPERCASE: bool = True
    REQUIRE_PASSWORD_LOWERCASE: bool = True
    REQUIRE_PASSWORD_DIGIT: bool = True
    REQUIRE_PASSWORD_SPECIAL: bool = True
    
    # Session
    SESSION_COOKIE_NAME: str = "session_id"
    SESSION_COOKIE_SECURE: bool = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SAMESITE: str = "lax"
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = "uploads"
    ALLOWED_FILE_EXTENSIONS: List[str] = [".pdf", ".docx", ".pptx", ".xlsx", ".txt", ".md"]
    
    # Vector Database
    CHROMA_DB_PATH: str = "./chroma_db"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields from .env
    
    @property
    def CORS_ORIGINS(self) -> List[str]:
        """Parse CORS origins from environment or use defaults"""
        cors_env = os.getenv("CORS_ORIGINS")
        if cors_env:
            try:
                import json
                return json.loads(cors_env)
            except:
                # If JSON parsing fails, split by comma
                return [origin.strip() for origin in cors_env.split(",")]
        return ["http://localhost:5173", "http://localhost:3000"]
    
    @property
    def ALLOWED_HOSTS(self) -> List[str]:
        """Parse allowed hosts from environment or use defaults"""
        hosts_env = os.getenv("ALLOWED_HOSTS")
        if hosts_env:
            return [host.strip() for host in hosts_env.split(",")]
        return ["localhost", "127.0.0.1"]


settings = Settings()
