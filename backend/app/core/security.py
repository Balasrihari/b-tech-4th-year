from datetime import datetime, timedelta
from typing import Optional
import re
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Truncate password to 72 bytes max for bcrypt compatibility
    if len(plain_password.encode('utf-8')) > 72:
        plain_password = plain_password[:72]
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    # Truncate password to 72 bytes max for bcrypt compatibility
    if len(password.encode('utf-8')) > 72:
        password = password[:72]
    return pwd_context.hash(password)


def validate_password_strength(password: str) -> tuple[bool, str]:
    """Validate password strength against security requirements"""
    if len(password) < settings.MIN_PASSWORD_LENGTH:
        return False, f"Password must be at least {settings.MIN_PASSWORD_LENGTH} characters long"
    
    if settings.REQUIRE_PASSWORD_UPPERCASE and not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if settings.REQUIRE_PASSWORD_LOWERCASE and not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if settings.REQUIRE_PASSWORD_DIGIT and not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    
    if settings.REQUIRE_PASSWORD_SPECIAL and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    
    return True, "Password meets requirements"


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "access":
            return None
        return payload
    except JWTError:
        return None


def decode_refresh_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "refresh":
            return None
        return payload
    except JWTError:
        return None


def sanitize_input(input_string: str) -> str:
    """Sanitize user input to prevent XSS attacks"""
    if not input_string:
        return ""
    
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>"\']', '', input_string)
    return sanitized.strip()
