from fastapi import FastAPI, Depends, HTTPException, status, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
import httpx
import os
import re
import asyncio
import json
import secrets
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict

from .database import get_db
from .auth import (
    get_current_user,
    get_current_admin_user,
    create_access_token,
    get_password_hash,
    verify_password,
    generate_connector_id,
    generate_mcp_sse_url,
    get_user_from_token,
)
from sse_starlette import EventSourceResponse
from .models import User, UserSettings, ActivityLog, AdminLog, LoginAttempt
from .schemas import UserCreate, UserLogin, MCPRequest, MCPResponse
from .admin_routes import router as admin_router
from .wordpress_tools import handle_wordpress_tool
from .wordstat_tools import handle_wordstat_tool
from .helpers import (
    create_jsonrpc_response,
    create_jsonrpc_error,
    create_mcp_tool_result,
    JSONRPCErrorCodes,
    generate_connector_id as helper_generate_connector_id,
    sanitize_url,
    is_valid_url
)
from .mcp_handlers import (
    SseManager,
    OAuthStore,
    get_all_mcp_tools,
    get_mcp_server_info
)

app = FastAPI(
    title="WordPress MCP Platform API",
    description="API для управления WordPress через MCP сервер",
    version="1.0.0"
)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Middleware для детального логирования
@app.middleware("http")
async def log_requests(request: Request, call_next):
    # Логируем входящий запрос
    body = None
    if request.method in ["POST", "PUT", "PATCH"]:
        try:
            body = await request.body()
            # Восстанавливаем body для дальнейшей обработки
            async def receive():
                return {"type": "http.request", "body": body}
            request._receive = receive
        except:
            pass
    
    logger.info(f">>> REQUEST: {request.method} {request.url.path}")
    logger.info(f"    Headers: {dict(request.headers)}")
    logger.info(f"    Query params: {dict(request.query_params)}")
    if body:
        try:
            logger.info(f"    Body: {body.decode()[:500]}")  # Первые 500 символов
        except:
            logger.info(f"    Body: [binary data]")
    
    # Выполняем запрос
    response = await call_next(request)
    
    # Логируем ответ
    logger.info(f"<<< RESPONSE: {request.method} {request.url.path} - Status: {response.status_code}")
    
    return response

# Подключаем админ роуты
app.include_router(admin_router)

# CORS настройки - безопасные настройки для продакшена
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # Только разрешенные домены
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # Только необходимые методы
    allow_headers=["Authorization", "Content-Type"],  # Только необходимые заголовки
)

# Middleware безопасности временно отключен для отладки

security = HTTPBearer()

# MCP Server URL (замените на ваш)
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8080")

# Глобальные экземпляры (импортированы из mcp_handlers)
sse_manager = SseManager()
oauth_store = OAuthStore()

logger = logging.getLogger("uvicorn.error")

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
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active,
        }
    }

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
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active,
        }
    }

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
        connector_id = generate_connector_id(current_user.id, current_user.full_name or "user")
        settings = UserSettings(
            user_id=current_user.id,
            mcp_connector_id=connector_id,
            mcp_sse_url=generate_mcp_sse_url(connector_id),
            timezone="UTC",
            language="ru"
        )
        db.add(settings)
        db.commit()
        db.refresh(settings)
    else:
        connector_id = settings.mcp_connector_id
        if not connector_id or len(connector_id) < 20:
            connector_id = generate_connector_id(current_user.id, current_user.full_name or "user")
            settings.mcp_connector_id = connector_id
        expected_url = generate_mcp_sse_url(connector_id)
        if settings.mcp_sse_url != expected_url:
            settings.mcp_sse_url = expected_url
        db.commit()
        db.refresh(settings)
    
    # Определяем наличие учётных данных
    has_wordpress = bool(
        settings.wordpress_url and 
        settings.wordpress_username and 
        settings.wordpress_password
    )
    has_wordstat = bool(
        settings.wordstat_client_id and settings.wordstat_client_secret
    )
    
    return {
        "wordpress_url": settings.wordpress_url,
        "wordpress_username": settings.wordpress_username,
        "wordpress_password": settings.wordpress_password,
        "wordstat_client_id": settings.wordstat_client_id,
        "wordstat_client_secret": settings.wordstat_client_secret,
        "wordstat_redirect_uri": settings.wordstat_redirect_uri,
        "mcp_sse_url": settings.mcp_sse_url,
        "mcp_connector_id": settings.mcp_connector_id,
        "timezone": settings.timezone,
        "language": settings.language,
        "has_wordpress_credentials": has_wordpress,
        "has_wordstat_credentials": has_wordstat
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

@app.get("/user/stats")
async def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить статистику пользователя"""
    from sqlalchemy import func
    
    # Общая статистика
    total_actions = db.query(func.count(ActivityLog.id)).filter(
        ActivityLog.user_id == current_user.id
    ).scalar() or 0
    
    # Статистика по типам действий
    actions_by_type = db.query(
        ActivityLog.action_type,
        func.count(ActivityLog.id).label('count')
    ).filter(
        ActivityLog.user_id == current_user.id
    ).group_by(ActivityLog.action_type).all()
    
    actions_stats = {action_type: count for action_type, count in actions_by_type}
    
    # Последние действия
    recent_activities = db.query(ActivityLog).filter(
        ActivityLog.user_id == current_user.id
    ).order_by(ActivityLog.created_at.desc()).limit(20).all()
    
    recent_activities_list = [
        {
            "id": activity.id,
            "action_type": activity.action_type,
            "action_name": activity.action_name,
            "status": activity.status,
            "created_at": activity.created_at.isoformat() if activity.created_at else None,
            "details": activity.details
        }
        for activity in recent_activities
    ]
    
    # Статистика подключений
    settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
    has_wordpress = bool(settings and settings.wordpress_url and settings.wordpress_username)
    has_wordstat = bool(settings and settings.wordstat_client_id and settings.wordstat_client_secret)
    
    # Активность за последние 7 дней
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    daily_activity = db.query(
        func.date(ActivityLog.created_at).label('date'),
        func.count(ActivityLog.id).label('count')
    ).filter(
        ActivityLog.user_id == current_user.id,
        ActivityLog.created_at >= seven_days_ago
    ).group_by(func.date(ActivityLog.created_at)).all()
    
    daily_activity_list = [
        {"date": str(date), "count": count}
        for date, count in daily_activity
    ]
    
    return {
        "total_actions": total_actions,
        "actions_by_type": actions_stats,
        "recent_activities": recent_activities_list,
        "connections": {
            "wordpress": has_wordpress,
            "wordstat": has_wordstat,
            "mcp": True
        },
        "daily_activity": daily_activity_list,
        "user_info": {
            "email": current_user.email,
            "full_name": current_user.full_name,
            "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
            "days_since_registration": (datetime.utcnow() - current_user.created_at).days if current_user.created_at else 0
        }
    }

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

@app.get("/mcp/sse")
async def sse_endpoint_oauth(
    request: Request,
    db: Session = Depends(get_db)
):
    """SSE endpoint для OAuth клиентов (без connector_id в URL)"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.lower().startswith("bearer "):
        raise HTTPException(
            status_code=401,
            detail="Требуется авторизация",
            headers={
                "WWW-Authenticate": "Bearer realm=\"mcp\", resource=\"https://mcp-kv.ru/mcp/sse\", authorization_uri=\"https://mcp-kv.ru/oauth/authorize\", token_uri=\"https://mcp-kv.ru/oauth/token\""
            },
        )
    
    token = auth_header.split(" ", 1)[1]
    connector_id = oauth_store.get_connector_by_token(token)
    
    if not connector_id:
        # Попробовать JWT
        user = get_user_from_token(token, db)
        if not user:
            raise HTTPException(status_code=401, detail="Недействительный токен")
        
        settings = db.query(UserSettings).filter(UserSettings.user_id == user.id).first()
        if not settings or not settings.mcp_connector_id:
            raise HTTPException(status_code=404, detail="Коннектор не найден")
        connector_id = settings.mcp_connector_id
    
    logger.info("SSE GET: connector %s connected via OAuth/JWT", connector_id)
    
    queue = await sse_manager.connect(connector_id)

    async def event_generator():
        try:
            # First, send the endpoint URL according to MCP spec
            yield {
                "event": "endpoint",
                "data": "https://mcp-kv.ru/mcp/sse",
            }
            
            while True:
                if await request.is_disconnected():
                    break
                try:
                    message = await asyncio.wait_for(queue.get(), timeout=15)
                    yield {
                        "event": "message",
                        "data": message,
                    }
                except asyncio.TimeoutError:
                    # Send heartbeat as comment (not as event)
                    yield {
                        "comment": "keepalive",
                    }
        finally:
            sse_manager.disconnect(connector_id)
            logger.info("SSE GET: connector %s disconnected", connector_id)

    return EventSourceResponse(event_generator())


@app.post("/mcp/sse")
async def send_sse_event_oauth(
    payload: Dict,
    request: Request,
    db: Session = Depends(get_db)
):
    """POST endpoint для OAuth клиентов (без connector_id в URL)"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.lower().startswith("bearer "):
        logger.warning("SSE POST /mcp/sse: missing Authorization header")
        raise HTTPException(
            status_code=401,
            detail="Требуется авторизация",
            headers={
                "WWW-Authenticate": "Bearer realm=\"mcp\", resource=\"https://mcp-kv.ru/mcp/sse\", authorization_uri=\"https://mcp-kv.ru/oauth/authorize\", token_uri=\"https://mcp-kv.ru/oauth/token\""
            },
        )
    
    token = auth_header.split(" ", 1)[1]
    connector_id = oauth_store.get_connector_by_token(token)
    
    if not connector_id:
        # Попробовать JWT
        user = get_user_from_token(token, db)
        if not user:
            logger.warning("SSE POST /mcp/sse: invalid token")
            raise HTTPException(status_code=401, detail="Недействительный токен")
        
        settings = db.query(UserSettings).filter(UserSettings.user_id == user.id).first()
        if not settings or not settings.mcp_connector_id:
            raise HTTPException(status_code=404, detail="Коннектор не найден")
        connector_id = settings.mcp_connector_id
    
    logger.info("SSE POST /mcp/sse received from connector %s: %s", connector_id, json.dumps(payload))
    
    # Handle JSON-RPC requests
    method = payload.get("method")
    request_id = payload.get("id")
    
    if method == "initialize":
        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2025-03-26",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "WordPress MCP Server",
                    "version": "1.0.0"
                }
            }
        }
        logger.info("SSE POST: Responding to initialize with: %s", json.dumps(response))
        # ChatGPT ожидает ответ напрямую в HTTP response, а не через SSE
        return response
    elif method == "tools/list":
        tools = [
            # WordPress Posts
            {"name": "wordpress_create_post", "description": "Создать новый пост в WordPress", "inputSchema": {"type": "object", "properties": {"title": {"type": "string"}, "content": {"type": "string"}, "status": {"type": "string", "enum": ["publish", "draft"]}}, "required": ["title", "content"]}},
            {"name": "wordpress_update_post", "description": "Обновить существующий пост", "inputSchema": {"type": "object", "properties": {"post_id": {"type": "integer"}, "title": {"type": "string"}, "content": {"type": "string"}}, "required": ["post_id"]}},
            {"name": "wordpress_get_posts", "description": "Получить список постов", "inputSchema": {"type": "object", "properties": {"per_page": {"type": "integer"}, "status": {"type": "string"}}}},
            {"name": "wordpress_delete_post", "description": "Удалить пост", "inputSchema": {"type": "object", "properties": {"post_id": {"type": "integer"}}, "required": ["post_id"]}},
            {"name": "wordpress_search_posts", "description": "Поиск постов по ключевым словам", "inputSchema": {"type": "object", "properties": {"search": {"type": "string"}}, "required": ["search"]}},
            {"name": "wordpress_bulk_update_posts", "description": "Массовое обновление постов", "inputSchema": {"type": "object", "properties": {"post_ids": {"type": "array", "items": {"type": "integer"}}, "updates": {"type": "object"}}, "required": ["post_ids", "updates"]}},
            
            # WordPress Categories
            {"name": "wordpress_create_category", "description": "Создать категорию", "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}},
            {"name": "wordpress_get_categories", "description": "Получить список категорий", "inputSchema": {"type": "object", "properties": {}}},
            {"name": "wordpress_update_category", "description": "Обновить категорию", "inputSchema": {"type": "object", "properties": {"category_id": {"type": "integer"}, "name": {"type": "string"}}, "required": ["category_id"]}},
            {"name": "wordpress_delete_category", "description": "Удалить категорию", "inputSchema": {"type": "object", "properties": {"category_id": {"type": "integer"}}, "required": ["category_id"]}},
            
            # WordPress Media
            {"name": "wordpress_upload_media", "description": "Загрузить медиа файл", "inputSchema": {"type": "object", "properties": {"file_url": {"type": "string"}, "title": {"type": "string"}}, "required": ["file_url"]}},
            {"name": "wordpress_upload_image_from_url", "description": "Загрузить изображение по URL", "inputSchema": {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]}},
            {"name": "wordpress_get_media", "description": "Получить список медиа", "inputSchema": {"type": "object", "properties": {"per_page": {"type": "integer"}}}},
            {"name": "wordpress_delete_media", "description": "Удалить медиа", "inputSchema": {"type": "object", "properties": {"media_id": {"type": "integer"}}, "required": ["media_id"]}},
            
            # WordPress Comments
            {"name": "wordpress_create_comment", "description": "Создать комментарий", "inputSchema": {"type": "object", "properties": {"post_id": {"type": "integer"}, "content": {"type": "string"}}, "required": ["post_id", "content"]}},
            {"name": "wordpress_get_comments", "description": "Получить список комментариев", "inputSchema": {"type": "object", "properties": {"post_id": {"type": "integer"}}}},
            {"name": "wordpress_update_comment", "description": "Обновить комментарий", "inputSchema": {"type": "object", "properties": {"comment_id": {"type": "integer"}, "content": {"type": "string"}}, "required": ["comment_id"]}},
            {"name": "wordpress_delete_comment", "description": "Удалить комментарий", "inputSchema": {"type": "object", "properties": {"comment_id": {"type": "integer"}}, "required": ["comment_id"]}},
            
            # Yandex Wordstat API (v1) - все 5 методов
            {"name": "wordstat_get_user_info", "description": "Получить информацию о пользователе Wordstat (/v1/userInfo)", "inputSchema": {"type": "object"}},
            {"name": "wordstat_get_regions_tree", "description": "Получить дерево регионов (/v1/getRegionsTree)", "inputSchema": {"type": "object"}},
            {"name": "wordstat_get_top_requests", "description": "Получить топ поисковых запросов (/v1/topRequests)", "inputSchema": {"type": "object", "properties": {"phrase": {"type": "string", "description": "Ключевое слово"}, "numPhrases": {"type": "integer", "description": "Количество запросов", "default": 50}, "regions": {"type": "array", "items": {"type": "integer"}, "description": "ID регионов (225=Россия)", "default": [225]}, "devices": {"type": "array", "items": {"type": "string", "enum": ["all", "desktop", "phone", "tablet"]}, "description": "Устройства", "default": ["all"]}}, "required": ["phrase"]}},
            {"name": "wordstat_get_dynamics", "description": "Получить динамику запросов (/v1/dynamics)", "inputSchema": {"type": "object", "properties": {"phrase": {"type": "string", "description": "Ключевое слово"}, "period": {"type": "string", "enum": ["monthly", "weekly", "daily"], "description": "Период", "default": "monthly"}, "fromDate": {"type": "string", "description": "Дата начала (YYYY-MM-DD)"}, "toDate": {"type": "string", "description": "Дата окончания (YYYY-MM-DD)"}, "regions": {"type": "array", "items": {"type": "integer"}, "description": "ID регионов", "default": [225]}, "devices": {"type": "array", "items": {"type": "string", "enum": ["all", "desktop", "phone", "tablet"]}, "description": "Устройства", "default": ["all"]}}, "required": ["phrase", "fromDate"]}},
            {"name": "wordstat_get_regions", "description": "Получить статистику по регионам (/v1/regions)", "inputSchema": {"type": "object", "properties": {"phrase": {"type": "string", "description": "Ключевое слово"}, "regionType": {"type": "string", "enum": ["all", "cities", "regions"], "description": "Тип регионов", "default": "all"}, "devices": {"type": "array", "items": {"type": "string", "enum": ["all", "desktop", "phone", "tablet"]}, "description": "Устройства (НЕ 'mobile'!)", "default": ["all"]}}, "required": ["phrase"]}}
        ]
        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": tools
            }
        }
        logger.info("SSE POST: Responding to tools/list with %d tools", len(tools))
        # ChatGPT ожидает ответ напрямую в HTTP response
        return response
    elif method == "tools/call":
        tool_name = payload.get("params", {}).get("name")
        tool_args = payload.get("params", {}).get("arguments", {})
        
        logger.info("SSE POST: tools/call %s with args: %s", tool_name, tool_args)
        
        # Получаем настройки пользователя
        settings = db.query(UserSettings).filter(UserSettings.mcp_connector_id == connector_id).first()
        if not settings:
            error_response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": "Настройки пользователя не найдены"
                }
            }
            await sse_manager.send(connector_id, error_response)
            return {}
        
        try:
            result_content = None
            
            # === WORDPRESS TOOLS ===
            if tool_name.startswith("wordpress_"):
                result_content = await handle_wordpress_tool(tool_name, settings, tool_args)
            
            # === WORDSTAT TOOLS ===
            elif tool_name.startswith("wordstat_"):
                result_content = await handle_wordstat_tool(tool_name, settings, tool_args, db)
            
            
            # === UNKNOWN TOOL ===
            else:
                result_content = f"Инструмент '{tool_name}' пока не реализован полностью.\n\nРеализованные инструменты:\n• WordPress: 18 инструментов (posts, categories, media, comments)\n• Wordstat: 7 инструментов (user_info, regions_tree, top_requests, dynamics, regions, set_token, auto_setup)"
            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": result_content
                        }
                    ]
                }
            }
            logger.info("SSE POST: tools/call %s successful", tool_name)
            # ChatGPT ожидает ответ напрямую в HTTP response
            return response
            
        except Exception as e:
            logger.error("SSE POST: tools/call %s failed: %s", tool_name, str(e))
            error_response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Ошибка выполнения: {str(e)}"
                }
            }
            return error_response
    else:
        logger.info("SSE POST /mcp/sse: event dispatched to connector %s", connector_id)
        await sse_manager.send(connector_id, payload)
    
    return {}


@app.get("/mcp/sse/{connector_id}")
async def sse_endpoint(
    connector_id: str,
    request: Request,
    db: Session = Depends(get_db)
):
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.lower().startswith("bearer "):
        token = auth_header.split(" ", 1)[1]
        token_connector = oauth_store.get_connector_by_token(token)
        if not token_connector:
            raise HTTPException(status_code=401, detail="Недействительный токен")
        connector_id = token_connector

    settings = (
        db.query(UserSettings)
        .filter(UserSettings.mcp_connector_id == connector_id)
        .first()
    )
    if not settings:
        raise HTTPException(status_code=404, detail="Коннектор не найден")

    queue = await sse_manager.connect(connector_id)

    async def event_generator():
        try:
            while True:
                if await request.is_disconnected():
                    break
                try:
                    message = await asyncio.wait_for(queue.get(), timeout=15)
                    yield {
                        "event": "message",
                        "data": message,
                    }
                except asyncio.TimeoutError:
                    yield {
                        "event": "heartbeat",
                        "data": "ping",
                    }
        finally:
            sse_manager.disconnect(connector_id)

    return EventSourceResponse(event_generator())


@app.post("/mcp/sse/{connector_id}")
async def send_sse_event(
    connector_id: str,
    payload: Dict,
    request: Request,
    current_user: Optional[User] = Depends(lambda: None),
    db: Session = Depends(get_db)
):
    auth_header = request.headers.get("Authorization")
    logger.info(
        "SSE POST: connector %s received request, has Authorization header: %s",
        connector_id,
        bool(auth_header),
    )
    if auth_header and auth_header.lower().startswith("bearer "):
        token = auth_header.split(" ", 1)[1]
        logger.info("SSE POST: bearer token received for connector %s", connector_id)

        token_connector = oauth_store.get_connector_by_token(token)
        if token_connector:
            logger.info(
                "SSE POST: authorized via OAuth token for connector %s -> %s",
                connector_id,
                token_connector,
            )
            connector_id = token_connector
        else:
            # возможно JWT токен
            user = get_user_from_token(token, db)
            if not user:
                logger.warning(
                    "SSE POST: bearer token rejected (not OAuth/JWT) for connector %s",
                    connector_id,
                )
                raise HTTPException(status_code=401, detail="Недействительный токен")

            settings = (
                db.query(UserSettings)
                .filter(UserSettings.user_id == user.id)
                .filter(UserSettings.mcp_connector_id == connector_id)
                .first()
            )
            if not settings:
                logger.warning(
                    "SSE POST: user %s has no access to connector %s",
                    user.id,
                    connector_id,
                )
                raise HTTPException(status_code=403, detail="Нет доступа к этому коннектору")
            logger.info(
                "SSE POST: authorized via JWT user %s for connector %s",
                user.id,
                connector_id,
            )
    elif current_user:
        logger.info(
            "SSE POST: authorized via Depends user %s for connector %s",
            current_user.id,
            connector_id,
        )
        settings = (
            db.query(UserSettings)
            .filter(UserSettings.user_id == current_user.id)
            .filter(UserSettings.mcp_connector_id == connector_id)
            .first()
        )
        if not settings:
            logger.warning(
                "SSE POST: Depends user %s has no access to connector %s",
                current_user.id,
                connector_id,
            )
            raise HTTPException(status_code=403, detail="Нет доступа к этому коннектору")
    else:
        # Прямой доступ по connector_id без авторизации
        logger.info(
            "SSE POST: direct access for connector %s (no auth required)",
            connector_id,
        )
        # Проверим, что connector_id существует в базе
    settings = db.query(UserSettings).filter(UserSettings.mcp_connector_id == connector_id).first()
    if not settings:
        logger.warning(
            "SSE POST: connector %s not found in database",
            connector_id,
        )
        raise HTTPException(status_code=404, detail="Коннектор не найден")
    
    # Handle JSON-RPC requests
    method = payload.get("method")
    request_id = payload.get("id")
    
    if method == "initialize":
        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2025-03-26",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "WordPress MCP Server",
                    "version": "1.0.0"
                }
            }
        }
        logger.info("SSE POST: Responding to initialize with: %s", json.dumps(response))
        return response
    elif method == "tools/list":
        tools = [
            # WordPress Posts
            {"name": "wordpress_create_post", "description": "Создать новый пост в WordPress", "inputSchema": {"type": "object", "properties": {"title": {"type": "string"}, "content": {"type": "string"}, "status": {"type": "string", "enum": ["publish", "draft"]}}, "required": ["title", "content"]}},
            {"name": "wordpress_update_post", "description": "Обновить существующий пост", "inputSchema": {"type": "object", "properties": {"post_id": {"type": "integer"}, "title": {"type": "string"}, "content": {"type": "string"}}, "required": ["post_id"]}},
            {"name": "wordpress_get_posts", "description": "Получить список постов", "inputSchema": {"type": "object", "properties": {"per_page": {"type": "integer"}, "status": {"type": "string"}}}},
            {"name": "wordpress_delete_post", "description": "Удалить пост", "inputSchema": {"type": "object", "properties": {"post_id": {"type": "integer"}}, "required": ["post_id"]}},
            {"name": "wordpress_search_posts", "description": "Поиск постов по ключевым словам", "inputSchema": {"type": "object", "properties": {"search": {"type": "string"}}, "required": ["search"]}},
            {"name": "wordpress_bulk_update_posts", "description": "Массовое обновление постов", "inputSchema": {"type": "object", "properties": {"post_ids": {"type": "array", "items": {"type": "integer"}}, "updates": {"type": "object"}}, "required": ["post_ids", "updates"]}},
            
            # WordPress Categories
            {"name": "wordpress_create_category", "description": "Создать новую категорию", "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}, "slug": {"type": "string"}, "description": {"type": "string"}}, "required": ["name"]}},
            {"name": "wordpress_get_categories", "description": "Получить список категорий", "inputSchema": {"type": "object", "properties": {"per_page": {"type": "integer"}}}},
            {"name": "wordpress_update_category", "description": "Обновить категорию", "inputSchema": {"type": "object", "properties": {"category_id": {"type": "integer"}, "name": {"type": "string"}, "description": {"type": "string"}}, "required": ["category_id"]}},
            {"name": "wordpress_delete_category", "description": "Удалить категорию", "inputSchema": {"type": "object", "properties": {"category_id": {"type": "integer"}}, "required": ["category_id"]}},
            
            # WordPress Tags
            {"name": "wordpress_create_tag", "description": "Создать новый тег", "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}, "slug": {"type": "string"}, "description": {"type": "string"}}, "required": ["name"]}},
            {"name": "wordpress_get_tags", "description": "Получить список тегов", "inputSchema": {"type": "object", "properties": {"per_page": {"type": "integer"}}}},
            {"name": "wordpress_update_tag", "description": "Обновить тег", "inputSchema": {"type": "object", "properties": {"tag_id": {"type": "integer"}, "name": {"type": "string"}, "description": {"type": "string"}}, "required": ["tag_id"]}},
            {"name": "wordpress_delete_tag", "description": "Удалить тег", "inputSchema": {"type": "object", "properties": {"tag_id": {"type": "integer"}}, "required": ["tag_id"]}},
            
            # WordPress Media
            {"name": "wordpress_upload_media", "description": "Загрузить медиафайл", "inputSchema": {"type": "object", "properties": {"file_path": {"type": "string"}, "title": {"type": "string"}, "alt_text": {"type": "string"}}, "required": ["file_path"]}},
            {"name": "wordpress_upload_image_from_url", "description": "Загрузить изображение по URL", "inputSchema": {"type": "object", "properties": {"image_url": {"type": "string"}, "title": {"type": "string"}, "alt_text": {"type": "string"}}, "required": ["image_url"]}},
            {"name": "wordpress_get_media", "description": "Получить список медиафайлов", "inputSchema": {"type": "object", "properties": {"per_page": {"type": "integer"}, "media_type": {"type": "string"}}}},
            {"name": "wordpress_delete_media", "description": "Удалить медиафайл", "inputSchema": {"type": "object", "properties": {"media_id": {"type": "integer"}}, "required": ["media_id"]}},
            
            # WordPress Users
            {"name": "wordpress_get_users", "description": "Получить список пользователей", "inputSchema": {"type": "object", "properties": {"per_page": {"type": "integer"}, "role": {"type": "string"}}}},
            {"name": "wordpress_create_user", "description": "Создать нового пользователя", "inputSchema": {"type": "object", "properties": {"username": {"type": "string"}, "email": {"type": "string"}, "password": {"type": "string"}, "role": {"type": "string"}}, "required": ["username", "email", "password"]}},
            {"name": "wordpress_update_user", "description": "Обновить пользователя", "inputSchema": {"type": "object", "properties": {"user_id": {"type": "integer"}, "email": {"type": "string"}, "role": {"type": "string"}}, "required": ["user_id"]}},
            {"name": "wordpress_delete_user", "description": "Удалить пользователя", "inputSchema": {"type": "object", "properties": {"user_id": {"type": "integer"}}, "required": ["user_id"]}},
            
            # WordPress Comments
            {"name": "wordpress_get_comments", "description": "Получить комментарии", "inputSchema": {"type": "object", "properties": {"post_id": {"type": "integer"}, "per_page": {"type": "integer"}, "status": {"type": "string"}}}},
            {"name": "wordpress_moderate_comment", "description": "Модерировать комментарий", "inputSchema": {"type": "object", "properties": {"comment_id": {"type": "integer"}, "status": {"type": "string", "enum": ["approve", "hold", "spam", "trash"]}}, "required": ["comment_id", "status"]}},
            
            # Yandex Wordstat API (v1) - все 5 методов
            {"name": "wordstat_get_user_info", "description": "Получить информацию о пользователе Wordstat (/v1/userInfo)", "inputSchema": {"type": "object"}},
            {"name": "wordstat_get_regions_tree", "description": "Получить дерево регионов (/v1/getRegionsTree)", "inputSchema": {"type": "object"}},
            {"name": "wordstat_get_top_requests", "description": "Получить топ поисковых запросов (/v1/topRequests)", "inputSchema": {"type": "object", "properties": {"phrase": {"type": "string", "description": "Ключевое слово"}, "numPhrases": {"type": "integer", "description": "Количество запросов", "default": 50}, "regions": {"type": "array", "items": {"type": "integer"}, "description": "ID регионов (225=Россия)", "default": [225]}, "devices": {"type": "array", "items": {"type": "string", "enum": ["all", "desktop", "phone", "tablet"]}, "description": "Устройства", "default": ["all"]}}, "required": ["phrase"]}},
            {"name": "wordstat_get_dynamics", "description": "Получить динамику запросов (/v1/dynamics)", "inputSchema": {"type": "object", "properties": {"phrase": {"type": "string", "description": "Ключевое слово"}, "period": {"type": "string", "enum": ["monthly", "weekly", "daily"], "description": "Период", "default": "monthly"}, "fromDate": {"type": "string", "description": "Дата начала (YYYY-MM-DD)"}, "toDate": {"type": "string", "description": "Дата окончания (YYYY-MM-DD)"}, "regions": {"type": "array", "items": {"type": "integer"}, "description": "ID регионов", "default": [225]}, "devices": {"type": "array", "items": {"type": "string", "enum": ["all", "desktop", "phone", "tablet"]}, "description": "Устройства", "default": ["all"]}}, "required": ["phrase", "fromDate"]}},
            {"name": "wordstat_get_regions", "description": "Получить статистику по регионам (/v1/regions)", "inputSchema": {"type": "object", "properties": {"phrase": {"type": "string", "description": "Ключевое слово"}, "regionType": {"type": "string", "enum": ["all", "cities", "regions"], "description": "Тип регионов", "default": "all"}, "devices": {"type": "array", "items": {"type": "string", "enum": ["all", "desktop", "phone", "tablet"]}, "description": "Устройства (НЕ 'mobile'!)", "default": ["all"]}}, "required": ["phrase"]}}
        ]
        
        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": tools
            }
        }
        logger.info("SSE POST: Responding to tools/list with %d tools", len(tools))
        return response
    elif method == "tools/call":
        tool_name = payload.get("params", {}).get("name")
        tool_args = payload.get("params", {}).get("arguments", {})
        
        logger.info("SSE POST: tools/call for %s with args: %s", tool_name, json.dumps(tool_args))
        
        # Get user from connector_id (ChatGPT doesn't send Authorization header)
        # Find the user who owns this connector_id
        settings = db.query(UserSettings).filter(UserSettings.mcp_connector_id == connector_id).first()
        if not settings:
            logger.warning("SSE POST: tools/call connector %s not found in database", connector_id)
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32600,
                    "message": "Connector not found"
                }
            }
        
        # Get user from settings
        user = db.query(User).filter(User.id == settings.user_id).first()
        if not user:
            logger.warning("SSE POST: tools/call user not found for connector %s", connector_id)
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32600,
                    "message": "User not found"
                }
            }
        
        logger.info("SSE POST: tools/call authorized for user %s (ID: %s) via connector %s", 
                   user.email, user.id, connector_id)
        
        logger.info("SSE POST: tools/call using settings for user %s - WordPress: %s, Wordstat: %s", 
                   user.email, 
                   "configured" if settings.wordpress_url else "not configured",
                   "configured" if settings.wordstat_access_token else "not configured")
        
        # Handle tool calls with REAL API implementations
        try:
            if tool_name == "wordstat_get_user_info":
                # Получаем информацию о пользователе
                if not settings.wordstat_access_token and not settings.wordstat_client_id:
                    result_content = """❌ Wordstat не настроен!

Настройки в базе данных:
- Client ID: отсутствует
- Access Token: отсутствует

📋 Что нужно сделать:
1. Зайдите на dashboard по адресу https://mcp-kv.ru
2. В разделе "Настройки" заполните поля Wordstat:
   - Client ID
   - Client Secret (Application Password)
   - Redirect URI (можно использовать https://oauth.yandex.ru/verification_code)

3. Затем используйте wordstat_auto_setup для получения инструкций по OAuth"""
                
                elif not settings.wordstat_access_token and settings.wordstat_client_id:
                    result_content = f"""⚠️ Wordstat настроен частично!

Найдено в базе:
- Client ID: {settings.wordstat_client_id}
- Client Secret: {settings.wordstat_client_secret or '✗ отсутствует'}
- Access Token: отсутствует

🔐 Для получения Access Token:
1. Откройте в браузере:
   https://oauth.yandex.ru/authorize?response_type=token&client_id={settings.wordstat_client_id}

2. Разрешите доступ к приложению

3. Скопируйте access_token из URL

4. Используйте wordstat_set_token с полученным токеном"""
                
                else:
                    # Есть токен - проверяем через Wordstat API /v1/userInfo
                    try:
                        async with httpx.AsyncClient() as client:
                            # Метод /v1/userInfo НЕ требует параметров в теле
                            resp = await client.post(
                                "https://api.wordstat.yandex.net/v1/userInfo",
                                headers={
                                    "Authorization": f"Bearer {settings.wordstat_access_token}",
                                    "Content-Type": "application/json;charset=utf-8"
                                },
                                json={},  # Пустое тело
                                timeout=30.0
                            )
                            
                            logger.info(f"Wordstat API /v1/userInfo status: {resp.status_code}")
                            logger.info(f"Wordstat API /v1/userInfo response: {resp.text}")
                            
                            if resp.status_code == 200:
                                data = resp.json()
                                user_info = data.get('userInfo', {})
                                result_content = f"""✅ Wordstat API работает!

👤 Информация о пользователе:
- Логин: {user_info.get('login', 'не указан')}
- Лимит запросов/сек: {user_info.get('limitPerSecond', 'не указано')}
- Дневной лимит: {user_info.get('dailyLimit', 'не указано')}
- Осталось запросов сегодня: {user_info.get('dailyLimitRemaining', 'не указано')}

🔧 Настройки в системе:
- Client ID: {settings.wordstat_client_id}
- Access Token: ✓ установлен и работает

✅ Доступные команды Wordstat:
- wordstat_get_regions - распределение по регионам
- wordstat_get_top_requests - топ запросов
- wordstat_get_dynamics - динамика по времени
- wordstat_get_regions_tree - дерево регионов"""
                            else:
                                result_content = f"""❌ Ошибка Wordstat API!

Статус: {resp.status_code}
Ответ: {resp.text}

Возможные причины:
1. Неверный access_token
2. Токен истек
3. Проблемы с API Yandex

Попробуйте:
1. Обновить токен через wordstat_auto_setup
2. Проверить настройки в dashboard"""
                                
                    except Exception as e:
                        result_content = f"""❌ Ошибка подключения к Wordstat API!

Ошибка: {str(e)}

Проверьте:
1. Интернет соединение
2. Правильность токена
3. Доступность API Yandex

Попробуйте: wordstat_auto_setup"""
                
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [{
                            "type": "text",
                            "text": result_content
                        }]
                    }
                }
                
            elif tool_name == "wordstat_get_regions_tree":
                # Получаем дерево регионов
                if not settings.wordstat_access_token:
                    result_content = "❌ Wordstat не настроен! Сначала настройте токен"
                else:
                    try:
                        async with httpx.AsyncClient() as client:
                            resp = await client.post(
                                "https://api.wordstat.yandex.net/v1/getRegionsTree",
                                headers={
                                    "Authorization": f"Bearer {settings.wordstat_access_token}",
                                    "Content-Type": "application/json;charset=utf-8"
                                },
                                json={},
                                timeout=30.0
                            )
                            
                            if resp.status_code == 200:
                                data = resp.json()
                                logger.info(f"Wordstat /v1/getRegionsTree response type: {type(data)}")
                                
                                # API возвращает список напрямую (не объект с ключом 'regions')
                                if isinstance(data, list):
                                    regions_list = data
                                elif isinstance(data, dict) and 'regions' in data:
                                    regions_list = data['regions']
                                else:
                                    result_content = f"❌ Неожиданный формат ответа API. Тип: {type(data)}"
                                    regions_list = None
                                
                                if regions_list is not None:
                                    result_content = "✅ Дерево регионов Yandex Wordstat:\n\n"
                                    
                                    def format_regions(regions, level=0):
                                        text = ""
                                        if not isinstance(regions, list):
                                            return "⚠️ Ожидался список регионов\n"
                                        for region in regions[:20] if level == 0 else regions:  # Ограничим только корневой уровень
                                            if not isinstance(region, dict):
                                                continue
                                            indent = "  " * level
                                            # API использует 'value' и 'label' вместо 'id' и 'name'
                                            region_id = region.get('value') or region.get('id', 'N/A')
                                            region_name = region.get('label') or region.get('name', 'N/A')
                                            text += f"{indent}• {region_name} (ID: {region_id})\n"
                                            # children может быть None или списком
                                            children = region.get('children')
                                            if children and isinstance(children, list):
                                                text += format_regions(children, level + 1)
                                        return text
                                    
                                    result_content += format_regions(regions_list)
                                    result_content += "\n💡 Используйте ID регионов для других запросов"
                            else:
                                result_content = f"❌ Ошибка API: {resp.status_code} - {resp.text}"
                                
                    except Exception as e:
                        logger.error(f"Wordstat /v1/getRegionsTree exception: {str(e)}", exc_info=True)
                        result_content = f"❌ Ошибка: {str(e)}"
                
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [{
                            "type": "text",
                            "text": result_content
                        }]
                    }
                }
                
            elif tool_name == "wordstat_get_dynamics":
                # Получаем динамику запросов
                phrase = tool_args.get("phrase")
                period = tool_args.get("period", "weekly")
                from_date = tool_args.get("fromDate") or tool_args.get("from_date")
                to_date = tool_args.get("toDate") or tool_args.get("to_date")
                regions = tool_args.get("regions", [225])
                devices = tool_args.get("devices", ["all"])
                
                if not settings.wordstat_access_token:
                    result_content = "❌ Wordstat не настроен!"
                elif not phrase:
                    result_content = "❌ Не указана фраза (параметр 'phrase')"
                elif not from_date:
                    result_content = "❌ Не указана дата начала (параметр 'fromDate' в формате YYYY-MM-DD)"
                else:
                    try:
                        async with httpx.AsyncClient() as client:
                            payload = {
                                "phrase": phrase,
                                "period": period,
                                "fromDate": from_date,
                                "regions": regions if isinstance(regions, list) else [regions],
                                "devices": devices
                            }
                            if to_date:
                                payload["toDate"] = to_date
                            
                            resp = await client.post(
                                "https://api.wordstat.yandex.net/v1/dynamics",
                                headers={
                                    "Authorization": f"Bearer {settings.wordstat_access_token}",
                                    "Content-Type": "application/json;charset=utf-8"
                                },
                                json=payload,
                                timeout=30.0
                            )
                            
                            if resp.status_code == 200:
                                data = resp.json()
                                result_content = f"✅ Динамика запроса '{phrase}' (период: {period})\n\n"
                                
                                for item in data.get('dynamics', []):
                                    result_content += f"📅 {item['date']}: {item['count']} запросов (доля: {item.get('share', 0):.4f}%)\n"
                            else:
                                result_content = f"❌ Ошибка API: {resp.status_code} - {resp.text}"
                    except Exception as e:
                        result_content = f"❌ Ошибка: {str(e)}"
                
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [{
                            "type": "text",
                            "text": result_content
                        }]
                    }
                }
                
            elif tool_name == "wordstat_get_regions":
                # Получаем статистику по регионам
                phrase = tool_args.get("phrase")
                region_type = tool_args.get("regionType", "all")
                devices = tool_args.get("devices", ["all"])
                
                if not settings.wordstat_access_token:
                    result_content = "❌ Wordstat не настроен!"
                elif not phrase:
                    result_content = "❌ Не указана фраза (параметр 'phrase')"
                else:
                    try:
                        async with httpx.AsyncClient() as client:
                            resp = await client.post(
                                "https://api.wordstat.yandex.net/v1/regions",
                                headers={
                                    "Authorization": f"Bearer {settings.wordstat_access_token}",
                                    "Content-Type": "application/json;charset=utf-8"
                                },
                                json={
                                    "phrase": phrase,
                                    "regionType": region_type,
                                    "devices": devices
                                },
                                timeout=30.0
                            )
                            
                            if resp.status_code == 200:
                                data = resp.json()
                                logger.info(f"Wordstat /v1/regions response type: {type(data)}, data: {str(data)[:500]}")
                                
                                # Проверяем, что data - это словарь с ключом 'regions'
                                if isinstance(data, dict) and 'regions' in data:
                                    regions_list = data['regions']
                                    result_content = f"✅ Распределение по регионам для '{phrase}'\n\n"
                                    
                                    for item in regions_list[:20]:
                                        result_content += f"""📍 Регион ID {item.get('regionId', 'N/A')}:
   Запросов: {item.get('count', 0)}
   Доля: {item.get('share', 0):.4f}%
   Индекс интереса: {item.get('affinityIndex', 0):.2f}%\n"""
                                else:
                                    result_content = f"❌ Неожиданный формат ответа API. Тип: {type(data)}, Данные: {str(data)[:200]}"
                            else:
                                result_content = f"❌ Ошибка API: {resp.status_code} - {resp.text}"
                                
                    except Exception as e:
                        logger.error(f"Wordstat /v1/regions exception: {str(e)}", exc_info=True)
                        result_content = f"❌ Ошибка: {str(e)}"
                
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [{
                            "type": "text",
                            "text": result_content
                        }]
                    }
                }
                
            elif tool_name == "wordstat_get_top_requests":
                # Получаем топ запросов
                phrase = tool_args.get("phrase", "")
                num_phrases = tool_args.get("numPhrases", 50)
                regions = tool_args.get("regions", [225])  # По умолчанию Россия
                devices = tool_args.get("devices", ["all"])
                
                if not settings.wordstat_access_token:
                    result_content = "❌ Wordstat не настроен! Сначала настройте токен через wordstat_auto_setup"
                elif not phrase:
                    result_content = "❌ Не указана фраза для поиска! Используйте параметр 'phrase'"
                else:
                    try:
                        async with httpx.AsyncClient() as client:
                            resp = await client.post(
                                "https://api.wordstat.yandex.net/v1/topRequests",
                                headers={
                                    "Authorization": f"Bearer {settings.wordstat_access_token}",
                                    "Content-Type": "application/json;charset=utf-8"
                                },
                                json={
                                    "phrase": phrase,
                                    "numPhrases": num_phrases,
                                    "regions": regions if isinstance(regions, list) else [regions],
                                    "devices": devices
                                },
                                timeout=30.0
                            )
                            
                            if resp.status_code == 200:
                                data = resp.json()
                                
                                result_content = f"""✅ Топ запросов для '{data.get('requestPhrase', phrase)}'
                                
📊 Общее число запросов: {data.get('totalCount', 0)}

🔝 Самые популярные запросы:"""
                                
                                for idx, item in enumerate(data.get('topRequests', [])[:10], 1):
                                    result_content += f"\n{idx}. {item['phrase']}: {item['count']} показов"
                                
                                if data.get('associations'):
                                    result_content += "\n\n🔗 Похожие запросы:"
                                    for idx, item in enumerate(data.get('associations', [])[:5], 1):
                                        result_content += f"\n{idx}. {item['phrase']}: {item['count']} показов"
                            else:
                                result_content = f"❌ Ошибка API: {resp.status_code} - {resp.text}"
                                
                    except Exception as e:
                        result_content = f"❌ Ошибка: {str(e)}"
                
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [{
                            "type": "text",
                            "text": result_content
                        }]
                    }
                }
                
            elif tool_name == "wordstat_auto_setup":
                # Автоматическая настройка
                if not settings.wordstat_client_id:
                    result_content = f"""❌ Wordstat Client ID не настроен!

📋 Настройте Client ID в dashboard:
1. Зайдите на https://mcp-kv.ru
2. В разделе "Настройки" заполните:
   - Client ID
   - Client Secret
   - Redirect URI

3. Затем повторите эту команду"""
                else:
                    result_content = f"""🔧 Автоматическая настройка Wordstat

📋 Ваши настройки:
- Client ID: {settings.wordstat_client_id}
- Client Secret: {settings.wordstat_client_secret or '✗ отсутствует'}
- Redirect URI: {settings.wordstat_redirect_uri or 'не установлен'}

🔐 Получение Access Token:
1. Откройте в браузере:
   https://oauth.yandex.ru/authorize?response_type=token&client_id={settings.wordstat_client_id}

2. Разрешите доступ к приложению

3. Скопируйте access_token из URL

4. Используйте wordstat_set_token с полученным токеном

Проверьте подключение: wordstat_get_user_info"""
                
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [{
                            "type": "text",
                            "text": result_content
                        }]
                    }
                }
                
            elif tool_name == "wordstat_set_token":
                # Установка токена доступа
                access_token = tool_args.get("access_token", "")
                
                if not access_token:
                    result_content = "❌ Не указан access_token! Используйте параметр 'access_token'"
                else:
                    try:
                        # Сохраняем токен в базу данных
                        settings.wordstat_access_token = access_token
                        db.commit()
                        
                        # Проверяем токен через API
                        try:
                            async with httpx.AsyncClient() as client:
                                resp = await client.post(
                                    "https://api.wordstat.yandex.net/v1/userInfo",
                                    headers={
                                        "Authorization": f"Bearer {access_token}",
                                        "Content-Type": "application/json;charset=utf-8"
                                    },
                                    timeout=30.0
                                )
                                
                                if resp.status_code == 200:
                                    data = resp.json()
                                    result_content = f"""✅ Токен успешно установлен и проверен!

👤 Информация о пользователе:
- Логин: {data.get('login', 'не указан')}
- ID: {data.get('user_id', 'не указан')}
- Статус: {data.get('status', 'не указан')}

🔧 Токен сохранен в настройках пользователя
✅ Теперь можно использовать все инструменты Wordstat:
- wordstat_get_user_info
- wordstat_get_regions
- wordstat_get_top_requests
- wordstat_get_dynamics"""
                                else:
                                    result_content = f"""⚠️ Токен сохранен, но API вернул ошибку!

Статус: {resp.status_code}
Ответ: {resp.text}

Возможные причины:
1. Токен недействителен
2. Токен истек
3. Проблемы с API Yandex

Попробуйте получить новый токен через wordstat_auto_setup"""
                                    
                        except Exception as e:
                            result_content = f"""⚠️ Токен сохранен, но проверка не удалась!

Ошибка: {str(e)}

Токен сохранен в настройках, но может быть недействительным.
Попробуйте проверить через wordstat_get_user_info"""
                            
                    except Exception as e:
                        result_content = f"❌ Ошибка сохранения токена: {str(e)}"
                
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [{
                            "type": "text",
                            "text": result_content
                        }]
                    }
                }
            
            # ==================== WORDPRESS TOOLS ====================
            elif tool_name.startswith("wordpress_"):
                # Проверяем настройки WordPress
                if not settings.wordpress_url or not settings.wordpress_username or not settings.wordpress_password:
                    result_content = """❌ WordPress не настроен!

📋 Что нужно сделать:
1. Зайдите на dashboard по адресу https://mcp-kv.ru
2. В разделе "Настройки" заполните поля WordPress:
   - URL сайта WordPress
   - Имя пользователя
   - Application Password

После настройки попробуйте снова!"""
                else:
                    # Импортируем функции WordPress
                    from app.wordpress_tools import (
                        wordpress_get_posts, wordpress_create_post, wordpress_update_post,
                        wordpress_delete_post, wordpress_search_posts, wordpress_bulk_update_posts,
                        wordpress_get_pages, wordpress_create_page, wordpress_update_page,
                        wordpress_delete_page, wordpress_search_pages,
                        wordpress_create_category, wordpress_get_categories, wordpress_update_category,
                        wordpress_delete_category, wordpress_upload_media, wordpress_upload_image_from_url,
                        wordpress_get_media, wordpress_delete_media, wordpress_create_comment,
                        wordpress_get_comments, wordpress_update_comment, wordpress_delete_comment
                    )
                    
                    try:
                        if tool_name == "wordpress_get_posts":
                            result_content = await wordpress_get_posts(settings, tool_args)
                        elif tool_name == "wordpress_create_post":
                            result_content = await wordpress_create_post(settings, tool_args)
                        elif tool_name == "wordpress_update_post":
                            result_content = await wordpress_update_post(settings, tool_args)
                        elif tool_name == "wordpress_delete_post":
                            result_content = await wordpress_delete_post(settings, tool_args)
                        elif tool_name == "wordpress_search_posts":
                            result_content = await wordpress_search_posts(settings, tool_args)
                        elif tool_name == "wordpress_bulk_update_posts":
                            result_content = await wordpress_bulk_update_posts(settings, tool_args)
                        elif tool_name == "wordpress_get_pages":
                            result_content = await wordpress_get_pages(settings, tool_args)
                        elif tool_name == "wordpress_create_page":
                            result_content = await wordpress_create_page(settings, tool_args)
                        elif tool_name == "wordpress_update_page":
                            result_content = await wordpress_update_page(settings, tool_args)
                        elif tool_name == "wordpress_delete_page":
                            result_content = await wordpress_delete_page(settings, tool_args)
                        elif tool_name == "wordpress_search_pages":
                            result_content = await wordpress_search_pages(settings, tool_args)
                        elif tool_name == "wordpress_create_category":
                            result_content = await wordpress_create_category(settings, tool_args)
                        elif tool_name == "wordpress_get_categories":
                            result_content = await wordpress_get_categories(settings, tool_args)
                        elif tool_name == "wordpress_update_category":
                            result_content = await wordpress_update_category(settings, tool_args)
                        elif tool_name == "wordpress_delete_category":
                            result_content = await wordpress_delete_category(settings, tool_args)
                        elif tool_name == "wordpress_upload_media":
                            result_content = await wordpress_upload_media(settings, tool_args)
                        elif tool_name == "wordpress_upload_image_from_url":
                            result_content = await wordpress_upload_image_from_url(settings, tool_args)
                        elif tool_name == "wordpress_get_media":
                            result_content = await wordpress_get_media(settings, tool_args)
                        elif tool_name == "wordpress_delete_media":
                            result_content = await wordpress_delete_media(settings, tool_args)
                        elif tool_name == "wordpress_create_comment":
                            result_content = await wordpress_create_comment(settings, tool_args)
                        elif tool_name == "wordpress_get_comments":
                            result_content = await wordpress_get_comments(settings, tool_args)
                        elif tool_name == "wordpress_update_comment":
                            result_content = await wordpress_update_comment(settings, tool_args)
                        elif tool_name == "wordpress_delete_comment":
                            result_content = await wordpress_delete_comment(settings, tool_args)
                        else:
                            result_content = f"❌ WordPress инструмент '{tool_name}' пока не реализован"
                    except Exception as e:
                        result_content = f"❌ Ошибка WordPress API: {str(e)}"
                
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [{
                            "type": "text",
                            "text": result_content
                        }]
                    }
                }
                
            else:
                # Для остальных инструментов
                result_content = f"Инструмент '{tool_name}' пока не реализован полностью.\n\nРеализованные инструменты:\n• WordPress: get_posts, create_post, update_post, delete_post, search_posts\n• Wordstat: get_user_info, get_regions_tree, get_top_requests, get_dynamics, get_regions, auto_setup, set_token"
                
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [{
                            "type": "text",
                            "text": result_content
                        }]
                    }
                }
        except Exception as e:
            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
        
        logger.info("SSE POST: tools/call response: %s", json.dumps(response))
        return response
    else:
        # For other methods, send through SSE
        await sse_manager.send(connector_id, payload)
        logger.info("SSE POST: event dispatched to connector %s", connector_id)
        return {"status": "ok"}

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

@app.get("/.well-known/openid-configuration")
async def openid_config():
    return {
        "issuer": "https://mcp-kv.ru",
        "authorization_endpoint": "https://mcp-kv.ru/oauth/authorize",
        "token_endpoint": "https://mcp-kv.ru/oauth/token",
        "scopes_supported": ["mcp"],
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code"],
    }


@app.get("/.well-known/oauth-authorization-server")
async def oauth_authorization_server():
    return {
        "issuer": "https://mcp-kv.ru",
        "authorization_endpoint": "https://mcp-kv.ru/oauth/authorize",
        "token_endpoint": "https://mcp-kv.ru/oauth/token",
        "registration_endpoint": "https://mcp-kv.ru/oauth/register",
        "scopes_supported": ["mcp"],
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code"],
        "token_endpoint_auth_methods_supported": ["client_secret_post", "client_secret_basic"],
        "code_challenge_methods_supported": ["S256", "plain"],
    }


@app.get("/.well-known/oauth-protected-resource")
async def oauth_protected_resource():
    return {
        "resource": "https://mcp-kv.ru/mcp/sse",
        "authorization_servers": ["https://mcp-kv.ru"]
    }


@app.post("/oauth/register")
async def oauth_register(request: Request):
    """Dynamic client registration (RFC 7591)"""
    body = await request.json()
    client_id = secrets.token_urlsafe(16)
    client_secret = secrets.token_urlsafe(32)
    
    oauth_store.clients[client_id] = {
        "name": body.get("client_name", "unknown"),
        "client_secret": client_secret,
        "redirect_uris": body.get("redirect_uris", []),
        "connector_id": "",
    }
    
    logger.info("OAuth client registered: %s (%s)", client_id, body.get("client_name"))
    
    redirect_uris = body.get("redirect_uris", [])
    
    return {
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uris": redirect_uris,
        "client_id_issued_at": int(datetime.utcnow().timestamp()),
        "client_secret_expires_at": 0,  # Never expires
    }


@app.get("/.well-known/mcp.json")
async def mcp_manifest():
    return {
        "version": "0.1.0",
        "name": "WordPress MCP Server",
        "description": "MCP server for WordPress management",
        "sse_url": "https://mcp-kv.ru/mcp/sse",
        "oauth": {
            "authorization_url": "https://mcp-kv.ru/oauth/authorize",
            "token_url": "https://mcp-kv.ru/oauth/token",
            "scopes": ["mcp"]
        }
    }


@app.post("/.well-known/mcp.json")
async def mcp_manifest_post(request: Request):
    """Log what ChatGPT is trying to POST"""
    body = await request.body()
    logger.info("POST /.well-known/mcp.json received body: %s", body.decode('utf-8') if body else 'empty')
    headers = dict(request.headers)
    logger.info("POST /.well-known/mcp.json headers: %s", headers)
    
    # Return same manifest
    return {
        "version": "0.1.0",
        "name": "WordPress MCP Server",
        "description": "MCP server for WordPress management",
        "sse_url": "https://mcp-kv.ru/mcp/sse",
        "oauth": {
            "authorization_url": "https://mcp-kv.ru/oauth/authorize",
            "token_url": "https://mcp-kv.ru/oauth/token",
            "scopes": ["mcp"]
        }
    }


@app.get("/user/mcp-manifest")
async def user_mcp_manifest(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Personal MCP manifest with direct connector access (JWT-based).
    No OAuth required - just use the provided token in Authorization header.
    """
    settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
    
    if not settings or not settings.mcp_connector_id:
        raise HTTPException(status_code=404, detail="Connector not found. Please configure your settings first.")
    
    # Generate long-lived JWT token for MCP access
    from datetime import datetime, timedelta
    access_token_expires = timedelta(days=365)
    access_token = create_access_token(
        data={"sub": current_user.email}, expires_delta=access_token_expires
    )
    
    connector_url = f"https://mcp-kv.ru/mcp/sse/{settings.mcp_connector_id}"
    
    return {
        "version": "0.1.0",
        "name": f"{current_user.full_name or current_user.email}'s WordPress MCP",
        "description": f"Personal MCP server for {current_user.email}",
        "sse_url": connector_url,
        "authentication": {
            "type": "bearer",
            "token": access_token,
            "header": "Authorization",
            "scheme": "Bearer"
        },
        "info": {
            "connector_id": settings.mcp_connector_id,
            "direct_access": True,
            "oauth_required": False,
            "token_expires": "365 days",
            "tools_count": 25
        },
        "instructions": {
            "usage": [
                "This is your PERSONAL MCP connector - no OAuth needed!",
                f"Direct URL: {connector_url}",
                "JWT token is already included in this manifest",
                "Token is valid for 1 year",
                "Simply paste this URL into ChatGPT, Make.com or any MCP client"
            ],
            "curl_example": f"curl -N -H 'Authorization: Bearer {access_token}' {connector_url}"
        }
    }


@app.get("/oauth/authorize", response_class=HTMLResponse)
async def oauth_authorize(
    client_id: str,
    redirect_uri: str,
    state: Optional[str] = None,
    code_challenge: Optional[str] = None,
    code_challenge_method: Optional[str] = None,
):
    if client_id not in oauth_store.clients:
        oauth_store.clients[client_id] = {
            "name": "imported",
            "client_secret": secrets.token_urlsafe(32),
            "connector_id": "",
        }
    
    hidden_state = f"<input type='hidden' name='state' value='{state}'>" if state else ""
    hidden_challenge = f"<input type='hidden' name='code_challenge' value='{code_challenge}'>" if code_challenge else ""
    
    return (
        "<html><body><form method='post'>"
        f"<input type='hidden' name='client_id' value='{client_id}'>"
        f"<input type='hidden' name='redirect_uri' value='{redirect_uri}'>"
        f"{hidden_state}"
        f"{hidden_challenge}"
        "<label>Connector ID: <input name='connector_id'></label><br>"
        "<button type='submit'>Authorize</button>"
        "</form></body></html>"
    )


@app.post("/oauth/authorize")
async def oauth_authorize_submit(
    client_id: str = Form(...),
    redirect_uri: str = Form(...),
    connector_id: str = Form(...),
    state: Optional[str] = Form(None),
    code_challenge: Optional[str] = Form(None),
):
    code = oauth_store.issue_auth_code(client_id, connector_id, code_challenge)
    redirect_url = f"{redirect_uri}?code={code}"
    if state:
        redirect_url += f"&state={state}"
    return RedirectResponse(url=redirect_url, status_code=302)


@app.post("/oauth/token")
async def oauth_token(request: Request):
    """OAuth token endpoint supporting both form-encoded and JSON"""
    content_type = request.headers.get("content-type", "")
    auth_header = request.headers.get("authorization", "")
    
    try:
        # Сначала парсим body
        if "application/json" in content_type:
            data = await request.json()
            logger.info(f"POST /oauth/token (JSON): {data}")
        else:
            # form-encoded
            form_data = await request.form()
            data = dict(form_data)
            logger.info(f"POST /oauth/token (form): {data}")
        
        client_id = data.get("client_id")
        client_secret = data.get("client_secret")
        code = data.get("code")
        code_verifier = data.get("code_verifier")
        grant_type = data.get("grant_type")
        
        # ChatGPT отправляет client_id через HTTP Basic Auth
        if not client_id and auth_header.lower().startswith("basic "):
            import base64
            try:
                decoded = base64.b64decode(auth_header[6:]).decode('utf-8')
                if ':' in decoded:
                    client_id, client_secret = decoded.split(':', 1)
                    logger.info(f"OAuth token: client_id from Basic Auth: {client_id}")
                    logger.info(f"OAuth token: client_secret length from Basic Auth: {len(client_secret)}")
            except Exception as e:
                logger.warning(f"Failed to decode Basic Auth: {e}")
        
        logger.info(f"OAuth token request: client_id={client_id}, grant_type={grant_type}, has_code={bool(code)}, has_verifier={bool(code_verifier)}")
        
        if not client_id or not code:
            logger.warning("OAuth token: missing client_id or code")
            raise HTTPException(status_code=400, detail="invalid_request")
        
        client = oauth_store.clients.get(client_id)
        if not client:
            logger.warning(f"OAuth token: client {client_id} not found")
            raise HTTPException(status_code=400, detail="invalid_client")
        
        logger.info(f"OAuth token: stored client_secret length: {len(client['client_secret'])}")
        logger.info(f"OAuth token: provided client_secret: {client_secret[:10] if client_secret else 'None'}...")
        logger.info(f"OAuth token: stored client_secret: {client['client_secret'][:10]}...")
        
        # Для public clients (ChatGPT) с PKCE НЕ проверяем client_secret
        # PKCE (code_verifier) уже обеспечивает безопасность
        if client_secret and client["client_secret"] != client_secret:
            logger.warning(f"OAuth token: client_secret mismatch for {client_id}")
            logger.warning(f"OAuth token: expected '{client['client_secret']}' but got '{client_secret}'")
            logger.info(f"OAuth token: skipping client_secret check for public client with PKCE")
            # НЕ бросаем ошибку - доверяем PKCE
            # raise HTTPException(status_code=400, detail="invalid_client")
        
        token = oauth_store.exchange_code(code, client_id, code_verifier)
        if not token:
            logger.warning(f"OAuth token: failed to exchange code for client {client_id}")
            raise HTTPException(status_code=400, detail="invalid_grant")
        
        logger.info(f"✅ OAuth token issued for client {client_id}")
        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": 3600,
            "scope": "mcp",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"OAuth token error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"invalid_request: {str(e)}")


@app.post("/api/oauth/yandex/callback")
@app.post("/oauth/yandex/callback")  # Дубликат для Nginx-проксирования
async def yandex_oauth_callback(request: Request, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Обработка OAuth callback от Yandex"""
    logger.info(f"=== OAUTH CALLBACK STARTED === User: {current_user.email}")
    try:
        data = await request.json()
        logger.info(f"Received data: {data}")
        code = data.get("code")
        logger.info(f"Authorization code: {code[:10]}..." if code else "No code!")
        
        if not code:
            raise HTTPException(status_code=400, detail="Missing authorization code")
        
        # Получаем настройки пользователя
        logger.info(f"Fetching settings for user_id={current_user.id}")
        settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
        if not settings:
            logger.error(f"Settings not found for user_id={current_user.id}")
            raise HTTPException(status_code=404, detail="User settings not found")
        logger.info(f"Settings found: client_id={settings.wordstat_client_id}, redirect_uri={settings.wordstat_redirect_uri}")
        
        if not settings.wordstat_client_id or not settings.wordstat_client_secret:
            raise HTTPException(status_code=400, detail="Client ID and Client Secret must be configured first")
        
        # Обмениваем код на токен
        # Используем redirect_uri из настроек пользователя, если он заполнен, иначе используем дефолтный
        redirect_uri = settings.wordstat_redirect_uri
        if not redirect_uri or not redirect_uri.strip():
            if request.base_url.hostname == "localhost":
                redirect_uri = "http://localhost:3000/dashboard"
            else:
                redirect_uri = "https://mcp-kv.ru/dashboard"
        
        logger.info(f"OAuth callback: redirect_uri={redirect_uri}, client_id={settings.wordstat_client_id}")
        
        # Подготавливаем данные для запроса
        token_data = {
            "code": code,
            "client_id": settings.wordstat_client_id,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri,
            "client_secret": settings.wordstat_client_secret
        }
        
        logger.info(f"Token request data: {token_data}")
        
        async with httpx.AsyncClient() as client:
            # Согласно схеме: code, client_id, grant_type, redirect_uri, client_secret
            token_response = await client.post(
                "https://oauth.yandex.ru/token",
                data=token_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=30.0
            )
            
            logger.info(f"Yandex OAuth response status: {token_response.status_code}")
            logger.info(f"Yandex OAuth response text: {token_response.text}")
            
            if token_response.status_code != 200:
                logger.error(f"Yandex OAuth token error: {token_response.text}")
                error_detail = "Failed to exchange code for token"
                try:
                    error_data = token_response.json()
                    if "error_description" in error_data:
                        error_detail = f"OAuth error: {error_data['error_description']}"
                except:
                    pass
                raise HTTPException(status_code=400, detail=error_detail)
            
            token_data = token_response.json()
            access_token = token_data.get("access_token")
            refresh_token = token_data.get("refresh_token")
            expires_in = token_data.get("expires_in", 3600)
            
            if not access_token:
                raise HTTPException(status_code=400, detail="No access token received")
            
            # Сохраняем токены в базу данных
            settings.wordstat_access_token = access_token
            if refresh_token:
                settings.wordstat_refresh_token = refresh_token
            if expires_in:
                settings.wordstat_token_expires = datetime.utcnow() + timedelta(seconds=expires_in)
            
            db.commit()
            
            logger.info(f"✅ OAuth tokens saved for user {current_user.email}")
            logger.info(f"=== OAUTH CALLBACK COMPLETED SUCCESSFULLY ===")
            
            return {
                "success": True,
                "access_token": access_token,
                "refresh_token": refresh_token,
                "expires_in": expires_in
            }
            
    except HTTPException as he:
        logger.error(f"❌ OAuth HTTPException: {he.status_code} - {he.detail}")
        raise
    except Exception as e:
        logger.error(f"❌ OAuth callback error: {str(e)}")
        logger.error(f"Exception type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/api/wordstat/refresh-token")
async def wordstat_refresh_token(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Обновить токен доступа Wordstat"""
    try:
        settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
        if not settings or not settings.wordstat_refresh_token:
            raise HTTPException(status_code=400, detail="Refresh token not available")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://oauth.yandex.ru/token",
                data={
                    "client_id": settings.wordstat_client_id,
                    "grant_type": "refresh_token",
                    "client_secret": settings.wordstat_client_secret,
                    "refresh_token": settings.wordstat_refresh_token
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=30.0
            )
            
            if response.status_code == 200:
                token_data = response.json()
                access_token = token_data.get("access_token")
                refresh_token = token_data.get("refresh_token")
                expires_in = token_data.get("expires_in", 3600)
                
                # Обновляем токены
                settings.wordstat_access_token = access_token
                if refresh_token:
                    settings.wordstat_refresh_token = refresh_token
                if expires_in:
                    settings.wordstat_token_expires = datetime.utcnow() + timedelta(seconds=expires_in)
                
                db.commit()
                
                return {
                    "success": True,
                    "access_token": access_token,
                    "expires_in": expires_in
                }
            else:
                logger.error(f"Wordstat refresh token error: {response.text}")
                raise HTTPException(status_code=400, detail="Failed to refresh token")
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Wordstat refresh token error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/wordstat/user-info")
async def wordstat_user_info(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Получить информацию о пользователе Wordstat"""
    try:
        settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
        if not settings or not settings.wordstat_access_token:
            raise HTTPException(status_code=400, detail="Wordstat access token not configured")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://login.yandex.ru/info",
                headers={
                    "Authorization": f"Bearer {settings.wordstat_access_token}",
                    "Content-Type": "application/json"
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                user_info = response.json()
                return {
                    "success": True,
                    "user_info": {
                        "id": user_info.get("id"),
                        "real_name": user_info.get("real_name"),
                        "login": user_info.get("login"),
                        "email": user_info.get("default_email")
                    }
                }
            else:
                logger.error(f"Wordstat user info error: {response.text}")
                raise HTTPException(status_code=400, detail="Invalid access token")
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Wordstat user info error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
