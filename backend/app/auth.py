from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError, jwt
import hashlib
import uuid
import os
import secrets
import bcrypt
from datetime import datetime, timedelta
from typing import Optional

from .database import get_db
from .models import User

# Настройки для JWT
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 24 * 60  # 24 часа

security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля с использованием bcrypt"""
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    """Хеширование пароля с использованием bcrypt"""
    # Генерируем соль и хешируем пароль
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def generate_connector_id(user_id: int, username: str) -> str:
    """Генерация уникального, ASCII-only ID коннектора для MCP SSE"""
    clean_username = "".join(
        c.lower() for c in username if c.isascii() and c.isalnum()
    )[:8]
    if not clean_username:
        clean_username = "user"
    random_id = secrets.token_urlsafe(24)  # 24 байта ~ 32 символа
    return f"{clean_username}-{random_id}"

def generate_mcp_sse_url(connector_id: str) -> str:
    """Генерация URL для MCP SSE сервера"""
    return f"https://mcp-kv.ru/mcp/sse/{connector_id}"


def get_user_from_token(token: str, db: Session) -> Optional[User]:
    """Получить пользователя по JWT токену, возвращает None если токен невалидный"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: Optional[str] = payload.get("sub")
        if not email:
            return None
    except JWTError:
        return None

    return db.query(User).filter(User.email == email).first()

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Создание JWT токена"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Получение текущего пользователя из JWT токена"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user
