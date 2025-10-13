from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session
import httpx
import os
import re
from typing import Optional

from .database import get_db
from .auth import get_current_user, create_access_token, get_password_hash, verify_password, generate_connector_id, generate_mcp_sse_url
from .models import User, UserSettings
from .schemas import UserCreate, UserLogin, MCPRequest, MCPResponse

app = FastAPI(
    title="WordPress MCP Platform API",
    description="API для управления WordPress через MCP сервер",
    version="1.0.0"
)

# CORS настройки - безопасные настройки для продакшена
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # Только разрешенные домены
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # Только необходимые методы
    allow_headers=["Authorization", "Content-Type"],  # Только необходимые заголовки
)

security = HTTPBearer()

# MCP Server URL (замените на ваш)
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8080")

# Функции валидации
def validate_email(email: str) -> bool:
    """Валидация email адреса"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password_strength(password: str) -> bool:
    """Валидация силы пароля"""
    if len(password) < 8:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'\d', password):
        return False
    return True

def sanitize_input(text: str) -> str:
    """Очистка входных данных от потенциально опасных символов"""
    if not text:
        return ""
    # Удаляем потенциально опасные символы
    dangerous_chars = ['<', '>', '"', "'", '&', ';', '(', ')', '|', '`', '$']
    for char in dangerous_chars:
        text = text.replace(char, '')
    return text.strip()

@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {"message": "WordPress MCP Platform API", "version": "1.0.0"}

@app.post("/auth/register")
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Регистрация нового пользователя"""
    # Валидация входных данных
    if not validate_email(user_data.email):
        raise HTTPException(
            status_code=400,
            detail="Некорректный email адрес"
        )
    
    if not validate_password_strength(user_data.password):
        raise HTTPException(
            status_code=400,
            detail="Пароль должен содержать минимум 8 символов, включая заглавные и строчные буквы, а также цифры"
        )
    
    # Очистка входных данных
    user_data.email = sanitize_input(user_data.email.lower())
    user_data.full_name = sanitize_input(user_data.full_name)
    
    # Проверяем, существует ли пользователь с таким email
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Пользователь с таким email уже существует"
        )
    
    # Создаем нового пользователя
    hashed_password = get_password_hash(user_data.password)
    user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Генерируем уникальный коннектор для MCP SSE
    connector_id = generate_connector_id(user.id, user.full_name)
    mcp_sse_url = generate_mcp_sse_url(connector_id)
    
    # Создаем настройки пользователя с коннектором
    settings = UserSettings(
        user_id=user.id,
        mcp_connector_id=connector_id,
        mcp_sse_url=mcp_sse_url,
        timezone="UTC",
        language="ru"
    )
    db.add(settings)
    db.commit()
    
    # Создаем токен доступа
    access_token = create_access_token(data={"sub": user.email})
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/auth/login")
async def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """Вход в систему"""
    # Валидация входных данных
    if not validate_email(login_data.email):
        raise HTTPException(
            status_code=400,
            detail="Некорректный email адрес"
        )
    
    # Очистка входных данных
    login_data.email = sanitize_input(login_data.email.lower())
    
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/auth/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Получить информацию о текущем пользователе"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "is_active": current_user.is_active
    }

@app.get("/user/settings")
async def get_user_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить настройки пользователя"""
    settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
    if not settings:
        raise HTTPException(status_code=404, detail="Настройки не найдены")
    
    return {
        "wordpress_url": settings.wordpress_url,
        "wordpress_username": settings.wordpress_username,
        "has_wordpress_credentials": bool(settings.wordpress_url and settings.wordpress_username),
        "has_wordstat_credentials": bool(settings.wordstat_client_id),
        "mcp_sse_url": settings.mcp_sse_url,
        "mcp_connector_id": settings.mcp_connector_id,
        "timezone": settings.timezone,
        "language": settings.language
    }

@app.put("/user/settings")
async def update_user_settings(
    settings_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Обновить настройки пользователя"""
    settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
    if not settings:
        settings = UserSettings(user_id=current_user.id)
        db.add(settings)
    
    # Валидация и очистка входных данных
    allowed_fields = [
        'wordpress_url', 'wordpress_username', 'wordpress_password',
        'wordstat_client_id', 'wordstat_client_secret', 'wordstat_redirect_uri',
        'timezone', 'language'
    ]
    
    for key, value in settings_data.items():
        if key in allowed_fields and hasattr(settings, key):
            # Очистка входных данных
            if isinstance(value, str):
                value = sanitize_input(value)
            setattr(settings, key, value)
    
    db.commit()
    return {"message": "Настройки обновлены"}

@app.post("/mcp/execute")
async def execute_mcp_command(
    request: MCPRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Выполнить команду MCP"""
    settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
    if not settings:
        raise HTTPException(status_code=404, detail="Настройки не найдены")
    
    # Подготавливаем параметры в зависимости от инструмента
    params = request.params.copy()
    
    if request.tool.startswith("wordpress_"):
        if not settings.wordpress_url:
            raise HTTPException(
                status_code=400,
                detail="Не настроены WordPress учетные данные"
            )
        params.update({
            "wordpress_url": settings.wordpress_url,
            "wordpress_username": settings.wordpress_username,
            "wordpress_password": settings.wordpress_password
        })
    elif request.tool.startswith("wordstat_"):
        if not settings.wordstat_client_id:
            raise HTTPException(
                status_code=400,
                detail="Не настроены Wordstat API учетные данные"
            )
        params.update({
            "client_id": settings.wordstat_client_id,
            "client_secret": settings.wordstat_client_secret
        })
    
    # Отправляем запрос к MCP серверу
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{MCP_SERVER_URL}/execute",
                json={
                    "tool": request.tool,
                    "params": params
                },
                timeout=30.0
            )
            response.raise_for_status()
            result = response.json()
            
            return MCPResponse(
                success=True,
                result=result,
                message="Команда выполнена успешно"
            )
        except httpx.RequestError as e:
            return MCPResponse(
                success=False,
                result=None,
                message=f"Ошибка подключения к MCP серверу: {str(e)}"
            )
        except httpx.HTTPStatusError as e:
            return MCPResponse(
                success=False,
                result=None,
                message=f"Ошибка MCP сервера: {e.response.status_code}"
            )

@app.get("/mcp/sse/{connector_id}")
async def get_mcp_sse_info(connector_id: str, db: Session = Depends(get_db)):
    """Получить информацию о MCP SSE коннекторе и проверить доступ"""
    settings = db.query(UserSettings).filter(UserSettings.mcp_connector_id == connector_id).first()
    if not settings:
        raise HTTPException(status_code=404, detail="Коннектор не найден")
    
    user = db.query(User).filter(User.id == settings.user_id).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=403, detail="Пользователь неактивен")
    
    return {
        "connector_id": connector_id,
        "user_id": user.id,
        "user_name": user.full_name,
        "available_tools": {
            "wordpress": [
                "create_post", "update_post", "get_posts", "delete_post", "search_posts",
                "create_category", "get_categories", "upload_media"
            ],
            "wordstat": [
                "get_wordstat_regions_tree", "get_wordstat_top_requests", "get_wordstat_dynamics"
            ],
            "google": [
                "google_trends", "google_search_volume", "google_keywords", "google_analytics"
            ],
        },
        "permissions": {
            "wordpress": bool(settings.wordpress_url),
            "wordstat": bool(settings.wordstat_client_id),
            "google": True  # Google работает через MCP сервер
        }
    }

@app.get("/mcp/tools")
async def get_available_tools():
    """Получить список доступных MCP инструментов"""
    return {
        "wordpress": [
            "create_post", "update_post", "get_posts", "delete_post", "search_posts",
            "bulk_update_posts", "create_category", "get_categories", "update_category",
            "delete_category", "upload_media", "upload_image_from_url", "get_media",
            "delete_media", "create_comment", "get_comments", "update_comment", "delete_comment"
        ],
        "wordstat": [
            "set_wordstat_token", "get_wordstat_regions_tree", "get_wordstat_top_requests",
            "get_wordstat_dynamics", "get_wordstat_regions", "get_wordstat_user_info",
            "auto_setup_wordstat"
        ],
    }
