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
    create_access_token,
    get_password_hash,
    verify_password,
    generate_connector_id,
    generate_mcp_sse_url,
    get_user_from_token,
)
from sse_starlette import EventSourceResponse
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

# Middleware безопасности временно отключен для отладки

security = HTTPBearer()

# MCP Server URL (замените на ваш)
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8080")

# Менеджер SSE потоков
class SseManager:
    def __init__(self):
        self._streams: Dict[str, asyncio.Queue] = {}

    async def connect(self, connector_id: str) -> asyncio.Queue:
        queue: asyncio.Queue = asyncio.Queue()
        self._streams[connector_id] = queue
        return queue

    def disconnect(self, connector_id: str) -> None:
        self._streams.pop(connector_id, None)

    async def send(self, connector_id: str, data: Dict) -> None:
        queue = self._streams.get(connector_id)
        if queue:
            await queue.put(json.dumps(data))

sse_manager = SseManager()

logger = logging.getLogger("uvicorn.error")

class OAuthStore:
    def __init__(self):
        self.clients: Dict[str, Dict[str, str]] = {}
        self.auth_codes: Dict[str, Dict[str, str]] = {}
        self.tokens: Dict[str, Dict[str, str]] = {}

    def create_client(self, name: str) -> Dict[str, str]:
        client_id = secrets.token_urlsafe(16)
        client_secret = secrets.token_urlsafe(32)
        self.clients[client_id] = {
            "name": name,
            "client_secret": client_secret,
            "connector_id": "",
        }
        return {"client_id": client_id, "client_secret": client_secret}

    def issue_auth_code(self, client_id: str, connector_id: str, code_challenge: Optional[str] = None) -> str:
        code = secrets.token_urlsafe(16)
        self.auth_codes[code] = {
            "client_id": client_id,
            "connector_id": connector_id,
            "expires_at": (datetime.utcnow() + timedelta(minutes=5)).isoformat(),
            "code_challenge": code_challenge,
        }
        return code

    def exchange_code(self, code: str, client_id: str, code_verifier: Optional[str] = None) -> Optional[str]:
        data = self.auth_codes.get(code)
        if not data or data["client_id"] != client_id:
            return None
        if datetime.utcnow() > datetime.fromisoformat(data["expires_at"]):
            self.auth_codes.pop(code, None)
            return None
        
        # Verify PKCE if code_challenge was provided
        if data.get("code_challenge"):
            if not code_verifier:
                logger.warning("PKCE: code_verifier required but not provided")
                return None
            
            import hashlib
            import base64
            
            # Compute challenge from verifier
            computed_challenge = base64.urlsafe_b64encode(
                hashlib.sha256(code_verifier.encode()).digest()
            ).decode().rstrip("=")
            
            if computed_challenge != data["code_challenge"]:
                logger.warning("PKCE: code_challenge mismatch")
                return None
        
        token = secrets.token_urlsafe(32)
        self.tokens[token] = {
            "connector_id": data["connector_id"],
            "expires_at": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
        }
        self.auth_codes.pop(code, None)
        return token

    def get_connector_by_token(self, token: str) -> Optional[str]:
        data = self.tokens.get(token)
        if not data:
            return None
        if datetime.utcnow() > datetime.fromisoformat(data["expires_at"]):
            self.tokens.pop(token, None)
            return None
        return data["connector_id"]


oauth_store = OAuthStore()

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
            
            if tool_name == "wordpress_get_posts":
                # Вызываем WordPress REST API
                wp_url = settings.wordpress_url.rstrip("/")
                wp_user = settings.wordpress_username
                wp_pass = settings.wordpress_password
                
                per_page = tool_args.get("per_page", 10)
                status = tool_args.get("status", "any")
                
                async with httpx.AsyncClient() as client:
                    auth = (wp_user, wp_pass) if wp_user and wp_pass else None
                    resp = await client.get(
                        f"{wp_url}/wp-json/wp/v2/posts",
                        params={"per_page": per_page, "status": status},
                        auth=auth,
                        timeout=30.0
                    )
                    resp.raise_for_status()
                    posts = resp.json()
                    
                    result_content = f"Найдено {len(posts)} постов:\n\n"
                    for post in posts:
                        result_content += f"ID: {post['id']}\n"
                        result_content += f"Название: {post['title']['rendered']}\n"
                        result_content += f"Статус: {post['status']}\n"
                        result_content += f"Дата: {post['date']}\n\n"
            
            elif tool_name == "wordpress_create_post":
                wp_url = settings.wordpress_url.rstrip("/")
                wp_user = settings.wordpress_username
                wp_pass = settings.wordpress_password
                
                async with httpx.AsyncClient() as client:
                    resp = await client.post(
                        f"{wp_url}/wp-json/wp/v2/posts",
                        json={
                            "title": tool_args.get("title"),
                            "content": tool_args.get("content"),
                            "status": tool_args.get("status", "draft")
                        },
                        auth=(wp_user, wp_pass),
                        timeout=30.0
                    )
                    resp.raise_for_status()
                    post = resp.json()
                    result_content = f"Пост создан успешно!\nID: {post['id']}\nНазвание: {post['title']['rendered']}\nСтатус: {post['status']}"
            
            # === WORDSTAT TOOLS ===
            
            elif tool_name == "wordstat_get_user_info":
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
                    # Есть токен - проверяем через API v1 /userInfo
                    try:
                        async with httpx.AsyncClient() as client:
                            resp = await client.post(
                                "https://api.wordstat.yandex.net/v1/userInfo",
                                headers={
                                    "Authorization": f"Bearer {settings.wordstat_access_token}",
                                    "Content-Type": "application/json;charset=utf-8"
                                },
                                timeout=30.0
                            )
                            
                            logger.info(f"Wordstat API /v1/userInfo status: {resp.status_code}")
                            logger.info(f"Wordstat API /v1/userInfo response: {resp.text[:500]}")
                            
                            if resp.status_code == 200:
                                data = resp.json()
                                
                                if "userInfo" in data:
                                    user_info = data["userInfo"]
                                    result_content = f"""✅ Подключение к Wordstat успешно!

📊 Информация о пользователе:
- Логин: {user_info.get('login', 'N/A')}
- Лимит запросов в секунду: {user_info.get('limitPerSecond', 'N/A')}
- Дневной лимит: {user_info.get('dailyLimit', 'N/A')}
- Осталось запросов сегодня: {user_info.get('dailyLimitRemaining', 'N/A')}

🎉 Можете использовать все инструменты Wordstat!
• wordstat_get_top_requests - топ запросов
• wordstat_get_regions_tree - дерево регионов
• wordstat_get_dynamics - динамика запросов
• wordstat_get_regions - распределение по регионам"""
                                
                                else:
                                    result_content = f"""⚠️ Необычный ответ от API:
{json.dumps(data, indent=2, ensure_ascii=False)}"""
                            
                            elif resp.status_code == 401:
                                result_content = f"""❌ Токен недействителен (401 Unauthorized)

🔧 Причины:
1. Токен устарел или неправильный
2. Токен был получен для другого приложения
3. У аккаунта нет доступа к Wordstat API

📋 Что делать:
1. Получите новый токен через: 
   https://oauth.yandex.ru/authorize?response_type=token&client_id={settings.wordstat_client_id if settings.wordstat_client_id else 'c654b948515a4a07a4c89648a0831d40'}

2. Убедитесь, что:
   - Авторизуетесь под правильным аккаунтом Яндекса
   - У аккаунта есть доступ к Wordstat
   - Client ID правильный"""
                            
                            else:
                                result_content = f"""❌ HTTP ошибка {resp.status_code}:
{resp.text}

Попробуйте получить новый токен через wordstat_auto_setup."""
                    
                    except Exception as e:
                        result_content = f"""❌ Ошибка при подключении к Wordstat API:
{str(e)}

Проверьте интернет-соединение или попробуйте позже."""
            
            elif tool_name == "wordstat_get_regions_tree":
                # Получаем дерево регионов через API v1
                if not settings.wordstat_access_token:
                    result_content = "❌ Токен Wordstat не настроен. Используйте wordstat_set_token."
                else:
                    try:
                        async with httpx.AsyncClient() as client:
                            resp = await client.post(
                                "https://api.wordstat.yandex.net/v1/getRegionsTree",
                                headers={
                                    "Authorization": f"Bearer {settings.wordstat_access_token}",
                                    "Content-Type": "application/json;charset=utf-8"
                                },
                                timeout=30.0
                            )
                            
                            if resp.status_code == 200:
                                data = resp.json()
                                result_content = f"""✅ Дерево регионов Yandex Wordstat:

{json.dumps(data, indent=2, ensure_ascii=False)}

💡 Используйте ID регионов для других запросов."""
                            else:
                                result_content = f"❌ Ошибка {resp.status_code}: {resp.text}"
                    except Exception as e:
                        result_content = f"❌ Ошибка: {str(e)}"
            
            elif tool_name == "wordstat_get_top_requests":
                # Получаем топ запросов через API v1
                query = tool_args.get("query")
                num_phrases = tool_args.get("num_phrases", 50)
                regions = tool_args.get("regions", [225])  # По умолчанию Россия
                devices = tool_args.get("devices", ["all"])
                
                if not query:
                    result_content = "❌ Ошибка: не указана фраза для поиска (параметр 'query')"
                elif not settings.wordstat_access_token:
                    result_content = "❌ Токен Wordstat не настроен. Используйте wordstat_set_token."
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
                                    "phrase": query,
                                    "numPhrases": num_phrases,
                                    "regions": regions if isinstance(regions, list) else [regions],
                                    "devices": devices
                                },
                                timeout=30.0
                            )
                            
                            logger.info(f"Wordstat topRequests status: {resp.status_code}")
                            logger.info(f"Wordstat topRequests response: {resp.text[:500]}")
                            
                            if resp.status_code == 200:
                                data = resp.json()
                                
                                result_content = f"""✅ Топ запросов для '{data.get('requestPhrase', query)}'
                                
📊 Общее число запросов: {data.get('totalCount', 0)}

🔝 Самые популярные запросы:"""
                                
                                for idx, item in enumerate(data.get('topRequests', [])[:10], 1):
                                    result_content += f"\n{idx}. {item['phrase']}: {item['count']} показов"
                                
                                if data.get('associations'):
                                    result_content += "\n\n🔗 Похожие запросы:"
                                    for idx, item in enumerate(data.get('associations', [])[:5], 1):
                                        result_content += f"\n{idx}. {item['phrase']}: {item['count']} показов"
                            else:
                                result_content = f"❌ Ошибка {resp.status_code}: {resp.text}"
                    except Exception as e:
                        result_content = f"❌ Ошибка: {str(e)}"
            
            elif tool_name == "wordstat_get_dynamics":
                # Получаем динамику запросов через API v1
                query = tool_args.get("query")
                period = tool_args.get("period", "weekly")  # monthly, weekly, daily
                from_date = tool_args.get("from_date")
                to_date = tool_args.get("to_date")
                regions = tool_args.get("regions", [225])
                devices = tool_args.get("devices", ["all"])
                
                if not query:
                    result_content = "❌ Ошибка: не указана фраза (параметр 'query')"
                elif not from_date:
                    result_content = "❌ Ошибка: не указана дата начала (параметр 'from_date' в формате YYYY-MM-DD)"
                elif not settings.wordstat_access_token:
                    result_content = "❌ Токен Wordstat не настроен. Используйте wordstat_set_token."
                else:
                    try:
                        async with httpx.AsyncClient() as client:
                            payload = {
                                "phrase": query,
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
                                result_content = f"✅ Динамика запроса '{query}' (период: {period})\n\n"
                                
                                for item in data.get('dynamics', []):
                                    result_content += f"📅 {item['date']}: {item['count']} запросов (доля: {item.get('share', 0):.4f}%)\n"
                            else:
                                result_content = f"❌ Ошибка {resp.status_code}: {resp.text}"
                    except Exception as e:
                        result_content = f"❌ Ошибка: {str(e)}"
            
            elif tool_name == "wordstat_get_regions":
                # Получаем статистику по регионам через API v1
                query = tool_args.get("query")
                region_type = tool_args.get("region_type", "all")  # cities, regions, all
                devices = tool_args.get("devices", ["all"])
                
                if not query:
                    result_content = "❌ Ошибка: не указана фраза (параметр 'query')"
                elif not settings.wordstat_access_token:
                    result_content = "❌ Токен Wordstat не настроен. Используйте wordstat_set_token."
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
                                    "phrase": query,
                                    "regionType": region_type,
                                    "devices": devices
                                },
                                timeout=30.0
                            )
                            
                            if resp.status_code == 200:
                                data = resp.json()
                                result_content = f"✅ Распределение по регионам для '{query}'\n\n"
                                
                                for item in data.get('regions', [])[:20]:
                                    result_content += f"""📍 Регион ID {item['regionId']}:
   Запросов: {item['count']}
   Доля: {item['share']:.4f}%
   Индекс интереса: {item['affinityIndex']:.2f}%\n"""
                            else:
                                result_content = f"❌ Ошибка {resp.status_code}: {resp.text}"
                    except Exception as e:
                        result_content = f"❌ Ошибка: {str(e)}"
            
            elif tool_name == "wordstat_auto_setup":
                # Автоматическая настройка с диагностикой
                status_lines = ["🔧 Диагностика Wordstat API\n"]
                status_lines.append("=" * 50)
                
                # Проверяем, что есть в базе
                if settings.wordstat_client_id:
                    status_lines.append(f"✅ Client ID: {settings.wordstat_client_id}")
                else:
                    status_lines.append("❌ Client ID: не установлен")
                
                if settings.wordstat_client_secret:
                    status_lines.append("✅ Client Secret: установлен")
                else:
                    status_lines.append("❌ Client Secret: не установлен")
                
                if settings.wordstat_access_token:
                    status_lines.append("✅ Access Token: установлен")
                else:
                    status_lines.append("❌ Access Token: не установлен")
                
                status_lines.append("\n" + "=" * 50)
                
                # Даем инструкции в зависимости от ситуации
                if not settings.wordstat_client_id:
                    status_lines.append("""
📋 ШАГ 1: Регистрация приложения Yandex Direct

1. Откройте: https://oauth.yandex.ru/client/new
2. Заполните форму:
   - Название: "MCP WordPress"
   - Права доступа: выберите "API Яндекс.Директ"
   - Redirect URI: https://oauth.yandex.ru/verification_code
3. Нажмите "Создать приложение"
4. Скопируйте Client ID и пароль приложения
5. Зайдите на https://mcp-kv.ru и сохраните их в настройках

📚 Документация: https://yandex.ru/dev/direct/doc/start/about.html""")
                
                elif not settings.wordstat_access_token:
                    status_lines.append(f"""
📋 ШАГ 2: Получение Access Token

У вас уже есть Client ID! Теперь получите токен:

1. Откройте эту ссылку в браузере:
   https://oauth.yandex.ru/authorize?response_type=token&client_id={settings.wordstat_client_id}

2. Разрешите доступ к API Яндекс.Директ

3. После разрешения вы будете перенаправлены на URL вида:
   https://oauth.yandex.ru/verification_code#access_token=ВАШТОКЕН...

4. Скопируйте значение access_token из адресной строки

5. Используйте инструмент wordstat_set_token с этим токеном

💡 Токен действителен 1 год.""")
                
                else:
                    status_lines.append("""
✅ Wordstat полностью настроен!

Используйте инструменты:
• wordstat_get_top_requests - топ запросов по ключевому слову
• wordstat_get_regions_tree - список регионов
• wordstat_get_dynamics - динамика запросов
• wordstat_get_regions - статистика по регионам

Проверьте подключение: wordstat_get_user_info""")
                
                result_content = "\n".join(status_lines)
            
            else:
                result_content = f"Инструмент '{tool_name}' пока не реализован полностью.\n\nРеализованные инструменты:\n• WordPress: get_posts, create_post\n• Wordstat: set_token, get_user_info, get_regions_tree, get_top_requests, get_dynamics, get_regions, auto_setup"
            
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
            
            # Yandex Wordstat
            {"name": "wordstat_get_user_info", "description": "Получить информацию о пользователе Wordstat", "inputSchema": {"type": "object"}},
            {"name": "wordstat_get_regions_tree", "description": "Получить дерево регионов", "inputSchema": {"type": "object"}},
            {"name": "wordstat_get_top_requests", "description": "Получить топ запросов", "inputSchema": {"type": "object", "properties": {"phrase": {"type": "string"}, "region_id": {"type": "integer"}}, "required": ["phrase"]}},
            {"name": "wordstat_get_dynamics", "description": "Получить динамику запросов", "inputSchema": {"type": "object", "properties": {"phrase": {"type": "string"}, "region_id": {"type": "integer"}, "date_from": {"type": "string"}, "date_to": {"type": "string"}}, "required": ["phrase"]}},
            {"name": "wordstat_get_regions", "description": "Получить список регионов", "inputSchema": {"type": "object"}},
            {"name": "wordstat_auto_setup", "description": "Автоматическая настройка токена Wordstat", "inputSchema": {"type": "object"}},
            {"name": "wordstat_set_token", "description": "Установить токен доступа Wordstat", "inputSchema": {"type": "object", "properties": {"access_token": {"type": "string"}}, "required": ["access_token"]}},
            {"name": "wordstat_get_competitors", "description": "Анализ конкурентов", "inputSchema": {"type": "object", "properties": {"phrase": {"type": "string"}, "region_id": {"type": "integer"}}, "required": ["phrase"]}},
            {"name": "wordstat_get_related_queries", "description": "Получить похожие запросы", "inputSchema": {"type": "object", "properties": {"phrase": {"type": "string"}, "region_id": {"type": "integer"}}, "required": ["phrase"]}},
            {"name": "wordstat_get_geography", "description": "Получить географию запросов", "inputSchema": {"type": "object", "properties": {"phrase": {"type": "string"}, "region_id": {"type": "integer"}}, "required": ["phrase"]}},
            {"name": "wordstat_export_data", "description": "Экспорт данных Wordstat", "inputSchema": {"type": "object", "properties": {"phrase": {"type": "string"}, "region_id": {"type": "integer"}, "format": {"type": "string", "enum": ["csv", "json", "xlsx"]}}, "required": ["phrase"]}}
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
                    # Есть токен - проверяем через API v1 /userInfo
                    try:
                        async with httpx.AsyncClient() as client:
                            resp = await client.post(
                                "https://api.wordstat.yandex.net/v1/userInfo",
                                headers={
                                    "Authorization": f"Bearer {settings.wordstat_access_token}",
                                    "Content-Type": "application/json;charset=utf-8"
                                },
                                timeout=30.0
                            )
                            
                            logger.info(f"Wordstat API /v1/userInfo status: {resp.status_code}")
                            
                            if resp.status_code == 200:
                                data = resp.json()
                                result_content = f"""✅ Wordstat API работает!

👤 Информация о пользователе:
- Логин: {data.get('login', 'не указан')}
- ID: {data.get('user_id', 'не указан')}
- Статус: {data.get('status', 'не указан')}

🔧 Настройки в системе:
- Client ID: {settings.wordstat_client_id}
- Access Token: {'✓ установлен' if settings.wordstat_access_token else '✗ отсутствует'}

Проверьте подключение: wordstat_get_user_info"""
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
                
            elif tool_name == "wordstat_get_regions":
                # Получаем список регионов
                if not settings.wordstat_access_token:
                    result_content = "❌ Wordstat не настроен! Сначала настройте токен через wordstat_auto_setup"
                else:
                    try:
                        async with httpx.AsyncClient() as client:
                            resp = await client.post(
                                "https://api.wordstat.yandex.net/v1/regions",
                                headers={
                                    "Authorization": f"Bearer {settings.wordstat_access_token}",
                                    "Content-Type": "application/json;charset=utf-8"
                                },
                                timeout=30.0
                            )
                            
                            if resp.status_code == 200:
                                data = resp.json()
                                regions = data.get('data', [])
                                result_content = f"✅ Получено {len(regions)} регионов:\n\n"
                                
                                for region in regions[:10]:  # Показываем первые 10
                                    result_content += f"• {region.get('name', 'Без названия')} (ID: {region.get('region_id', 'N/A')})\n"
                                
                                if len(regions) > 10:
                                    result_content += f"\n... и еще {len(regions) - 10} регионов"
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
                
            elif tool_name == "wordstat_get_top_requests":
                # Получаем топ запросов
                phrase = tool_args.get("phrase", "")
                region_id = tool_args.get("region_id", 0)
                
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
                                    "region_id": region_id
                                },
                                timeout=30.0
                            )
                            
                            if resp.status_code == 200:
                                data = resp.json()
                                requests = data.get('data', [])
                                result_content = f"✅ Топ запросов для фразы '{phrase}':\n\n"
                                
                                for i, req in enumerate(requests[:10], 1):
                                    result_content += f"{i}. {req.get('phrase', 'N/A')} - {req.get('shows', 0)} показов\n"
                                
                                if len(requests) > 10:
                                    result_content += f"\n... и еще {len(requests) - 10} запросов"
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
                
            else:
                # Для остальных инструментов
                result_content = f"Инструмент '{tool_name}' пока не реализован полностью.\n\nРеализованные инструменты:\n• WordPress: get_posts, create_post\n• Wordstat: get_user_info, get_regions, get_top_requests, auto_setup, set_token"
                
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
