from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import bcrypt

from .database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связь с настройками
    settings = relationship("UserSettings", back_populates="user", uselist=False)
    
    def verify_password(self, password: str) -> bool:
        """Проверка пароля"""
        return bcrypt.checkpw(password.encode('utf-8'), self.hashed_password.encode('utf-8'))

class UserSettings(Base):
    __tablename__ = "user_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, unique=True)
    
    # WordPress настройки
    wordpress_url = Column(String, nullable=True)
    wordpress_username = Column(String, nullable=True)
    wordpress_password = Column(String, nullable=True)  # Зашифрованный пароль
    
    # Wordstat API настройки
    wordstat_client_id = Column(String, nullable=True)
    wordstat_client_secret = Column(String, nullable=True)  # Зашифрованный секрет
    wordstat_redirect_uri = Column(String, nullable=True)
    wordstat_access_token = Column(Text, nullable=True)  # Зашифрованный токен
    wordstat_refresh_token = Column(Text, nullable=True)  # Зашифрованный токен
    
    # MCP SSE настройки
    mcp_sse_url = Column(String, nullable=True)
    mcp_connector_id = Column(String, nullable=True, unique=True)
    
    # Дополнительные настройки
    timezone = Column(String, default="UTC")
    language = Column(String, default="ru")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связь с пользователем
    user = relationship("User", back_populates="settings")
