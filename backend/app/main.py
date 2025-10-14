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
from datetime import datetime, timedelta
from typing import Optional, Dict

from .database import get_db
from .auth import get_current_user, create_access_token, get_password_hash, verify_password, generate_connector_id, generate_mcp_sse_url
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

    def issue_auth_code(self, client_id: str, connector_id: str) -> str:
        code = secrets.token_urlsafe(16)
        self.auth_codes[code] = {
            "client_id": client_id,
            "connector_id": connector_id,
            "expires_at": (datetime.utcnow() + timedelta(minutes=5)).isoformat(),
        }
        return code

    def exchange_code(self, code: str, client_id: str) -> Optional[str]:
        data = self.auth_codes.get(code)
        if not data or data["client_id"] != client_id:
            return None
        if datetime.utcnow() > datetime.fromisoformat(data["expires_at"]):
            self.auth_codes.pop(code, None)
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
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    settings = (
        db.query(UserSettings)
        .filter(UserSettings.user_id == current_user.id)
        .filter(UserSettings.mcp_connector_id == connector_id)
        .first()
    )
    if not settings:
        raise HTTPException(status_code=403, detail="Нет доступа к этому коннектору")

    await sse_manager.send(connector_id, payload)
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


@app.get("/oauth/authorize", response_class=HTMLResponse)
async def oauth_authorize(client_id: str, redirect_uri: str, state: Optional[str] = None):
    if client_id not in oauth_store.clients:
        oauth_store.clients[client_id] = {
            "name": "imported",
            "client_secret": secrets.token_urlsafe(32),
            "connector_id": "",
        }
    return (
        "<html><body><form method='post'>"
        "<label>Connector ID: <input name='connector_id'></label><br>"
        "<button type='submit'>Authorize</button>"
        "</form></body></html>"
    )


@app.post("/oauth/authorize")
async def oauth_authorize_submit(
    client_id: str = Form(...),
    redirect_uri: str = Form(...),
    state: Optional[str] = Form(None),
    connector_id: str = Form(...),
):
    code = oauth_store.issue_auth_code(client_id, connector_id)
    redirect_url = f"{redirect_uri}?code={code}"
    if state:
        redirect_url += f"&state={state}"
    return RedirectResponse(url=redirect_url, status_code=302)


@app.post("/oauth/token")
async def oauth_token(
    client_id: str = Form(...),
    client_secret: str = Form(...),
    code: str = Form(...),
    redirect_uri: str = Form(...),
):
    client = oauth_store.clients.get(client_id)
    if not client or client["client_secret"] != client_secret:
        raise HTTPException(status_code=400, detail="invalid_client")
    token = oauth_store.exchange_code(code, client_id)
    if not token:
        raise HTTPException(status_code=400, detail="invalid_grant")
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": 3600,
        "scope": "mcp",
    }
