"""
MCP Protocol Handlers
SSE, OAuth, и JSON-RPC handlers для Model Context Protocol
"""
import asyncio
import json
import secrets
import hashlib
import base64
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
import logging

logger = logging.getLogger(__name__)


# ==================== SSE MANAGER ====================

class SseManager:
    """
    Менеджер Server-Sent Events потоков
    Управляет WebSocket-подобными соединениями для MCP
    """
    
    def __init__(self):
        self._streams: Dict[str, asyncio.Queue] = {}
    
    async def connect(self, connector_id: str) -> asyncio.Queue:
        """
        Создание нового SSE соединения
        
        Args:
            connector_id: Уникальный ID коннектора
        
        Returns:
            asyncio.Queue для отправки сообщений
        """
        queue: asyncio.Queue = asyncio.Queue()
        self._streams[connector_id] = queue
        logger.info(f"SSE: New connection for connector {connector_id}")
        return queue
    
    def disconnect(self, connector_id: str) -> None:
        """
        Закрытие SSE соединения
        
        Args:
            connector_id: ID коннектора для отключения
        """
        self._streams.pop(connector_id, None)
        logger.info(f"SSE: Disconnected connector {connector_id}")
    
    async def send(self, connector_id: str, data: Dict) -> None:
        """
        Отправка данных через SSE
        
        Args:
            connector_id: ID получателя
            data: Данные для отправки (будут сериализованы в JSON)
        """
        queue = self._streams.get(connector_id)
        if queue:
            await queue.put(json.dumps(data))
        else:
            logger.warning(f"SSE: Attempted to send to disconnected connector {connector_id}")
    
    def is_connected(self, connector_id: str) -> bool:
        """
        Проверка активности соединения
        
        Args:
            connector_id: ID коннектора
        
        Returns:
            True если коннектор подключен
        """
        return connector_id in self._streams
    
    def get_active_connections(self) -> int:
        """
        Получить количество активных соединений
        
        Returns:
            Количество активных SSE соединений
        """
        return len(self._streams)


# ==================== OAUTH STORE ====================

class OAuthStore:
    """
    Хранилище OAuth данных (клиенты, коды, токены)
    In-memory реализация для простоты (в production использовать Redis/DB)
    """
    
    def __init__(self):
        self.clients: Dict[str, Dict[str, str]] = {}
        self.auth_codes: Dict[str, Dict[str, str]] = {}
        self.tokens: Dict[str, Dict[str, str]] = {}
    
    def create_client(self, name: str) -> Dict[str, str]:
        """
        Создание нового OAuth клиента
        
        Args:
            name: Название клиента
        
        Returns:
            Dict с client_id и client_secret
        """
        client_id = secrets.token_urlsafe(16)
        client_secret = secrets.token_urlsafe(32)
        
        self.clients[client_id] = {
            "name": name,
            "client_secret": client_secret,
            "connector_id": "",
        }
        
        logger.info(f"OAuth: Created client '{name}' with ID {client_id[:8]}...")
        
        return {
            "client_id": client_id,
            "client_secret": client_secret
        }
    
    def issue_auth_code(
        self,
        client_id: str,
        connector_id: str,
        code_challenge: Optional[str] = None
    ) -> str:
        """
        Выдача authorization code
        
        Args:
            client_id: ID клиента
            connector_id: ID коннектора для привязки
            code_challenge: PKCE challenge (optional)
        
        Returns:
            Authorization code
        """
        code = secrets.token_urlsafe(16)
        
        self.auth_codes[code] = {
            "client_id": client_id,
            "connector_id": connector_id,
            "expires_at": (datetime.utcnow() + timedelta(minutes=5)).isoformat(),
            "code_challenge": code_challenge,
        }
        
        logger.info(f"OAuth: Issued auth code for client {client_id[:8]}...")
        
        return code
    
    def exchange_code(
        self,
        code: str,
        client_id: str,
        code_verifier: Optional[str] = None
    ) -> Optional[str]:
        """
        Обмен authorization code на access token
        
        Args:
            code: Authorization code
            client_id: ID клиента
            code_verifier: PKCE verifier (если использовался challenge)
        
        Returns:
            Access token или None если код недействителен
        """
        data = self.auth_codes.get(code)
        
        # Проверка валидности кода
        if not data or data["client_id"] != client_id:
            logger.warning(f"OAuth: Invalid code or client_id mismatch")
            return None
        
        # Проверка expiration
        if datetime.utcnow() > datetime.fromisoformat(data["expires_at"]):
            self.auth_codes.pop(code, None)
            logger.warning(f"OAuth: Auth code expired")
            return None
        
        # Проверка PKCE если был использован
        if data.get("code_challenge"):
            if not code_verifier:
                logger.warning("OAuth PKCE: code_verifier required but not provided")
                return None
            
            # Вычисляем challenge из verifier
            computed_challenge = base64.urlsafe_b64encode(
                hashlib.sha256(code_verifier.encode()).digest()
            ).decode().rstrip("=")
            
            if computed_challenge != data["code_challenge"]:
                logger.warning("OAuth PKCE: code_challenge mismatch")
                return None
        
        # Генерируем access token
        token = secrets.token_urlsafe(32)
        self.tokens[token] = {
            "connector_id": data["connector_id"],
            "expires_at": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
        }
        
        # Удаляем использованный код
        self.auth_codes.pop(code, None)
        
        logger.info(f"OAuth: Exchanged code for token (connector: {data['connector_id']})")
        
        return token
    
    def get_connector_by_token(self, token: str) -> Optional[str]:
        """
        Получить connector_id по access token
        
        Args:
            token: Access token
        
        Returns:
            connector_id или None если токен недействителен
        """
        data = self.tokens.get(token)
        
        if not data:
            return None
        
        # Проверка expiration
        if datetime.utcnow() > datetime.fromisoformat(data["expires_at"]):
            self.tokens.pop(token, None)
            logger.info(f"OAuth: Token expired and removed")
            return None
        
        return data["connector_id"]
    
    def revoke_token(self, token: str) -> bool:
        """
        Отзыв access token
        
        Args:
            token: Token для отзыва
        
        Returns:
            True если токен был отозван
        """
        if token in self.tokens:
            self.tokens.pop(token)
            logger.info(f"OAuth: Token revoked")
            return True
        return False


# ==================== MCP TOOLS DEFINITIONS ====================

def get_wordpress_tools() -> list:
    """
    Получить список WordPress MCP tools
    
    Returns:
        List of tool definitions
    """
    return [
        {
            "name": "wordpress_get_posts",
            "description": "Получить список постов WordPress",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "per_page": {"type": "number", "description": "Количество постов"},
                    "status": {"type": "string", "description": "Статус постов (publish, draft, any)"}
                }
            }
        },
        {
            "name": "wordpress_create_post",
            "description": "Создать новый пост в WordPress",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Заголовок поста"},
                    "content": {"type": "string", "description": "Содержимое поста"},
                    "status": {"type": "string", "description": "Статус (draft, publish)"}
                },
                "required": ["title", "content"]
            }
        },
        {
            "name": "wordpress_update_post",
            "description": "Обновить существующий пост",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "post_id": {"type": "number", "description": "ID поста"},
                    "title": {"type": "string", "description": "Новый заголовок"},
                    "content": {"type": "string", "description": "Новое содержимое"},
                    "status": {"type": "string", "description": "Новый статус"}
                },
                "required": ["post_id"]
            }
        },
        {
            "name": "wordpress_delete_post",
            "description": "Удалить пост",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "post_id": {"type": "number", "description": "ID поста для удаления"}
                },
                "required": ["post_id"]
            }
        },
        {
            "name": "wordpress_search_posts",
            "description": "Поиск постов по ключевым словам",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "search": {"type": "string", "description": "Поисковый запрос"}
                },
                "required": ["search"]
            }
        },
        {
            "name": "wordpress_bulk_update_posts",
            "description": "Массовое обновление постов",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "post_ids": {"type": "array", "items": {"type": "number"}, "description": "Массив ID постов"},
                    "updates": {"type": "object", "description": "Объект с полями для обновления"}
                },
                "required": ["post_ids", "updates"]
            }
        },
        {
            "name": "wordpress_get_pages",
            "description": "Получить список страниц WordPress",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "per_page": {"type": "number", "description": "Количество страниц"},
                    "status": {"type": "string", "description": "Статус страниц (publish, draft, any)"}
                }
            }
        },
        {
            "name": "wordpress_create_page",
            "description": "Создать новую страницу в WordPress",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Заголовок страницы"},
                    "content": {"type": "string", "description": "Содержимое страницы"},
                    "status": {"type": "string", "description": "Статус (draft, publish)"},
                    "parent": {"type": "number", "description": "ID родительской страницы (опционально)"}
                },
                "required": ["title", "content"]
            }
        },
        {
            "name": "wordpress_update_page",
            "description": "Обновить существующую страницу",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "page_id": {"type": "number", "description": "ID страницы"},
                    "title": {"type": "string", "description": "Новый заголовок"},
                    "content": {"type": "string", "description": "Новое содержимое"},
                    "status": {"type": "string", "description": "Новый статус"},
                    "parent": {"type": "number", "description": "ID родительской страницы"}
                },
                "required": ["page_id"]
            }
        },
        {
            "name": "wordpress_delete_page",
            "description": "Удалить страницу",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "page_id": {"type": "number", "description": "ID страницы для удаления"}
                },
                "required": ["page_id"]
            }
        },
        {
            "name": "wordpress_search_pages",
            "description": "Поиск страниц по ключевым словам",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "search": {"type": "string", "description": "Поисковый запрос"}
                },
                "required": ["search"]
            }
        },
        {
            "name": "wordpress_create_category",
            "description": "Создать категорию",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Название категории"}
                },
                "required": ["name"]
            }
        },
        {
            "name": "wordpress_get_categories",
            "description": "Получить список категорий",
            "inputSchema": {"type": "object", "properties": {}}
        },
        {
            "name": "wordpress_update_category",
            "description": "Обновить категорию",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "category_id": {"type": "number", "description": "ID категории"},
                    "name": {"type": "string", "description": "Новое название"}
                },
                "required": ["category_id", "name"]
            }
        },
        {
            "name": "wordpress_delete_category",
            "description": "Удалить категорию",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "category_id": {"type": "number", "description": "ID категории"}
                },
                "required": ["category_id"]
            }
        },
        {
            "name": "wordpress_upload_media",
            "description": "Загрузить медиафайл по URL",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "file_url": {"type": "string", "description": "URL файла"},
                    "title": {"type": "string", "description": "Название файла"}
                },
                "required": ["file_url"]
            }
        },
        {
            "name": "wordpress_upload_image_from_url",
            "description": "Загрузить изображение по URL",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL изображения"}
                },
                "required": ["url"]
            }
        },
        {
            "name": "wordpress_get_media",
            "description": "Получить список медиафайлов",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "per_page": {"type": "number", "description": "Количество файлов"}
                }
            }
        },
        {
            "name": "wordpress_delete_media",
            "description": "Удалить медиафайл",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "media_id": {"type": "number", "description": "ID медиафайла"}
                },
                "required": ["media_id"]
            }
        },
        {
            "name": "wordpress_create_comment",
            "description": "Создать комментарий",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "post_id": {"type": "number", "description": "ID поста"},
                    "content": {"type": "string", "description": "Текст комментария"}
                },
                "required": ["post_id", "content"]
            }
        },
        {
            "name": "wordpress_get_comments",
            "description": "Получить комментарии",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "post_id": {"type": "number", "description": "ID поста (опционально)"}
                }
            }
        },
        {
            "name": "wordpress_update_comment",
            "description": "Обновить комментарий",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "comment_id": {"type": "number", "description": "ID комментария"},
                    "content": {"type": "string", "description": "Новый текст"}
                },
                "required": ["comment_id", "content"]
            }
        },
        {
            "name": "wordpress_delete_comment",
            "description": "Удалить комментарий",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "comment_id": {"type": "number", "description": "ID комментария"}
                },
                "required": ["comment_id"]
            }
        }
    ]


def get_wordstat_tools() -> list:
    """
    Получить список Wordstat MCP tools
    
    Returns:
        List of tool definitions
    """
    return [
        {
            "name": "wordstat_set_token",
            "description": "Установить токен Yandex Wordstat",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "token": {"type": "string", "description": "Access token от Yandex OAuth"}
                },
                "required": ["token"]
            }
        },
        {
            "name": "wordstat_get_user_info",
            "description": "Получить информацию об аккаунте Wordstat",
            "inputSchema": {"type": "object", "properties": {}}
        },
        {
            "name": "wordstat_get_regions_tree",
            "description": "Получить дерево регионов Yandex",
            "inputSchema": {"type": "object", "properties": {}}
        },
        {
            "name": "wordstat_get_top_requests",
            "description": "Получить топ запросов по ключевому слову",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "phrase": {"type": "string", "description": "Ключевое слово"},
                    "numPhrases": {"type": "number", "description": "Количество фраз (1-100)"},
                    "regions": {"type": "array", "items": {"type": "number"}, "description": "Массив ID регионов"},
                    "devices": {"type": "array", "items": {"type": "string"}, "description": "Устройства (all, mobile, desktop)"}
                },
                "required": ["phrase"]
            }
        },
        {
            "name": "wordstat_get_dynamics",
            "description": "Получить динамику запросов по фразе",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "phrase": {"type": "string", "description": "Ключевое слово"},
                    "regions": {"type": "array", "items": {"type": "number"}, "description": "Массив ID регионов"},
                    "devices": {"type": "array", "items": {"type": "string"}, "description": "Устройства"}
                },
                "required": ["phrase"]
            }
        },
        {
            "name": "wordstat_get_regions",
            "description": "Получить статистику по регионам",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "phrase": {"type": "string", "description": "Ключевое слово"},
                    "regions": {"type": "array", "items": {"type": "number"}, "description": "Массив ID регионов"},
                    "devices": {"type": "array", "items": {"type": "string"}, "description": "Устройства"}
                },
                "required": ["phrase"]
            }
        },
        {
            "name": "wordstat_auto_setup",
            "description": "Автоматическая настройка подключения Wordstat с диагностикой",
            "inputSchema": {"type": "object", "properties": {}}
        }
    ]


def get_all_mcp_tools() -> list:
    """
    Получить полный список всех MCP tools
    
    Returns:
        Объединённый список WordPress + Wordstat tools
    """
    return get_wordpress_tools() + get_wordstat_tools()


# ==================== MCP PROTOCOL INFO ====================

def get_mcp_server_info() -> Dict[str, Any]:
    """
    Получить информацию о MCP сервере
    
    Returns:
        Server info dict для MCP initialize response
    """
    return {
        "protocolVersion": "2025-03-26",
        "capabilities": {
            "tools": {}
        },
        "serverInfo": {
            "name": "WordPress MCP Server",
            "version": "1.0.0"
        }
    }

