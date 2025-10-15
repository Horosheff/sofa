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
        },
        {
            "name": "wordpress_get_tags",
            "description": "Получить список тегов WordPress",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "per_page": {"type": "number", "description": "Количество тегов"}
                }
            }
        },
        {
            "name": "wordpress_create_tag",
            "description": "Создать новый тег",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Название тега"},
                    "slug": {"type": "string", "description": "URL slug"},
                    "description": {"type": "string", "description": "Описание тега"}
                },
                "required": ["name"]
            }
        },
        {
            "name": "wordpress_update_tag",
            "description": "Обновить существующий тег",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "tag_id": {"type": "number", "description": "ID тега"},
                    "name": {"type": "string", "description": "Новое название"},
                    "description": {"type": "string", "description": "Новое описание"}
                },
                "required": ["tag_id"]
            }
        },
        {
            "name": "wordpress_delete_tag",
            "description": "Удалить тег",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "tag_id": {"type": "number", "description": "ID тега для удаления"}
                },
                "required": ["tag_id"]
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
            "name": "wordpress_moderate_comment",
            "description": "Модерировать комментарий (изменить статус)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "comment_id": {"type": "number", "description": "ID комментария"},
                    "status": {"type": "string", "description": "Новый статус (approve, hold, spam, trash)"}
                },
                "required": ["comment_id", "status"]
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
        }
    ]


def get_telegram_tools() -> list:
    """
    Получить список Telegram MCP tools
    
    Returns:
        List of tool definitions
    """
    return [
        {
            "name": "telegram_create_bot",
            "description": "Создать и настроить Telegram бота",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "bot_token": {
                        "type": "string",
                        "description": "Токен бота от @BotFather"
                    }
                },
                "required": ["bot_token"]
            }
        },
        {
            "name": "telegram_send_message",
            "description": "Отправить текстовое сообщение в чат",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "chat_id": {
                        "type": "string",
                        "description": "ID чата или username"
                    },
                    "text": {
                        "type": "string",
                        "description": "Текст сообщения"
                    },
                    "parse_mode": {
                        "type": "string",
                        "description": "Режим парсинга (HTML, Markdown)",
                        "default": "HTML"
                    }
                },
                "required": ["chat_id", "text"]
            }
        },
        {
            "name": "telegram_send_photo",
            "description": "Отправить фото в чат",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "chat_id": {
                        "type": "string",
                        "description": "ID чата или username"
                    },
                    "photo": {
                        "type": "string",
                        "description": "URL фото или file_id"
                    },
                    "caption": {
                        "type": "string",
                        "description": "Подпись к фото"
                    }
                },
                "required": ["chat_id", "photo"]
            }
        },
        {
            "name": "telegram_set_webhook",
            "description": "Установить webhook для бота",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL для webhook"
                    }
                },
                "required": ["url"]
            }
        },
        {
            "name": "telegram_get_bot_info",
            "description": "Получить информацию о боте",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        },
        {
            "name": "telegram_get_updates",
            "description": "Получить обновления бота",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "offset": {
                        "type": "integer",
                        "description": "Смещение для получения обновлений"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Максимальное количество обновлений"
                    }
                }
            }
        },
        {
            "name": "telegram_send_document",
            "description": "Отправить документ в чат",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "chat_id": {
                        "type": "string",
                        "description": "ID чата или username"
                    },
                    "document": {
                        "type": "string",
                        "description": "URL документа или file_id"
                    },
                    "caption": {
                        "type": "string",
                        "description": "Подпись к документу"
                    }
                },
                "required": ["chat_id", "document"]
            }
        },
        {
            "name": "telegram_delete_webhook",
            "description": "Удалить webhook бота",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        },
        {
            "name": "telegram_get_webhook_info",
            "description": "Получить информацию о webhook",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        },
        {
            "name": "telegram_set_commands",
            "description": "Установить команды бота",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "commands": {
                        "type": "array",
                        "description": "Список команд",
                        "items": {
                            "type": "object",
                            "properties": {
                                "command": {"type": "string"},
                                "description": {"type": "string"}
                            }
                        }
                    }
                },
                "required": ["commands"]
            }
        },
        {
            "name": "telegram_get_commands",
            "description": "Получить список команд бота",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        },
        {
            "name": "telegram_delete_message",
            "description": "Удалить сообщение",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "chat_id": {
                        "type": "string",
                        "description": "ID чата"
                    },
                    "message_id": {
                        "type": "integer",
                        "description": "ID сообщения"
                    }
                },
                "required": ["chat_id", "message_id"]
            }
        },
        {
            "name": "telegram_edit_message",
            "description": "Редактировать сообщение",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "chat_id": {
                        "type": "string",
                        "description": "ID чата"
                    },
                    "message_id": {
                        "type": "integer",
                        "description": "ID сообщения"
                    },
                    "text": {
                        "type": "string",
                        "description": "Новый текст"
                    }
                },
                "required": ["chat_id", "message_id", "text"]
            }
        },
        {
            "name": "telegram_pin_message",
            "description": "Закрепить сообщение",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "chat_id": {
                        "type": "string",
                        "description": "ID чата"
                    },
                    "message_id": {
                        "type": "integer",
                        "description": "ID сообщения"
                    }
                },
                "required": ["chat_id", "message_id"]
            }
        },
        {
            "name": "telegram_unpin_message",
            "description": "Открепить сообщение",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "chat_id": {
                        "type": "string",
                        "description": "ID чата"
                    }
                },
                "required": ["chat_id"]
            }
        },
        {
            "name": "telegram_get_chat",
            "description": "Получить информацию о чате",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "chat_id": {
                        "type": "string",
                        "description": "ID чата"
                    }
                },
                "required": ["chat_id"]
            }
        },
        {
            "name": "telegram_get_chat_member",
            "description": "Получить информацию об участнике чата",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "chat_id": {
                        "type": "string",
                        "description": "ID чата"
                    },
                    "user_id": {
                        "type": "integer",
                        "description": "ID пользователя"
                    }
                },
                "required": ["chat_id", "user_id"]
            }
        },
        {
            "name": "telegram_ban_chat_member",
            "description": "Заблокировать участника чата",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "chat_id": {
                        "type": "string",
                        "description": "ID чата"
                    },
                    "user_id": {
                        "type": "integer",
                        "description": "ID пользователя"
                    }
                },
                "required": ["chat_id", "user_id"]
            }
        },
        {
            "name": "telegram_unban_chat_member",
            "description": "Разблокировать участника чата",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "chat_id": {
                        "type": "string",
                        "description": "ID чата"
                    },
                    "user_id": {
                        "type": "integer",
                        "description": "ID пользователя"
                    }
                },
                "required": ["chat_id", "user_id"]
            }
        },
        {
            "name": "telegram_promote_chat_member",
            "description": "Повысить участника чата до администратора",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "chat_id": {
                        "type": "string",
                        "description": "ID чата"
                    },
                    "user_id": {
                        "type": "integer",
                        "description": "ID пользователя"
                    }
                },
                "required": ["chat_id", "user_id"]
            }
        },
        {
            "name": "telegram_restrict_chat_member",
            "description": "Ограничить права участника чата",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "chat_id": {
                        "type": "string",
                        "description": "ID чата"
                    },
                    "user_id": {
                        "type": "integer",
                        "description": "ID пользователя"
                    }
                },
                "required": ["chat_id", "user_id"]
            }
        },
        {
            "name": "telegram_export_chat_invite_link",
            "description": "Создать ссылку-приглашение в чат",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "chat_id": {
                        "type": "string",
                        "description": "ID чата"
                    }
                },
                "required": ["chat_id"]
            }
        },
        {
            "name": "telegram_create_chat_invite_link",
            "description": "Создать ссылку-приглашение в чат с настройками",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "chat_id": {
                        "type": "string",
                        "description": "ID чата"
                    },
                    "expire_date": {
                        "type": "integer",
                        "description": "Дата истечения (Unix timestamp)"
                    },
                    "member_limit": {
                        "type": "integer",
                        "description": "Лимит участников"
                    }
                },
                "required": ["chat_id"]
            }
        },
        {
            "name": "telegram_revoke_chat_invite_link",
            "description": "Отозвать ссылку-приглашение",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "chat_id": {
                        "type": "string",
                        "description": "ID чата"
                    },
                    "invite_link": {
                        "type": "string",
                        "description": "Ссылка-приглашение"
                    }
                },
                "required": ["chat_id", "invite_link"]
            }
        },
        {
            "name": "telegram_approve_chat_join_request",
            "description": "Одобрить заявку на вступление в чат",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "chat_id": {
                        "type": "string",
                        "description": "ID чата"
                    },
                    "user_id": {
                        "type": "integer",
                        "description": "ID пользователя"
                    }
                },
                "required": ["chat_id", "user_id"]
            }
        },
        {
            "name": "telegram_decline_chat_join_request",
            "description": "Отклонить заявку на вступление в чат",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "chat_id": {
                        "type": "string",
                        "description": "ID чата"
                    },
                    "user_id": {
                        "type": "integer",
                        "description": "ID пользователя"
                    }
                },
                "required": ["chat_id", "user_id"]
            }
        },
        {
            "name": "telegram_set_chat_photo",
            "description": "Установить фото чата",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "chat_id": {
                        "type": "string",
                        "description": "ID чата"
                    },
                    "photo": {
                        "type": "string",
                        "description": "URL фото или file_id"
                    }
                },
                "required": ["chat_id", "photo"]
            }
        },
        {
            "name": "telegram_delete_chat_photo",
            "description": "Удалить фото чата",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "chat_id": {
                        "type": "string",
                        "description": "ID чата"
                    }
                },
                "required": ["chat_id"]
            }
        },
        {
            "name": "telegram_set_chat_title",
            "description": "Установить название чата",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "chat_id": {
                        "type": "string",
                        "description": "ID чата"
                    },
                    "title": {
                        "type": "string",
                        "description": "Новое название"
                    }
                },
                "required": ["chat_id", "title"]
            }
        },
        {
            "name": "telegram_set_chat_description",
            "description": "Установить описание чата",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "chat_id": {
                        "type": "string",
                        "description": "ID чата"
                    },
                    "description": {
                        "type": "string",
                        "description": "Новое описание"
                    }
                },
                "required": ["chat_id", "description"]
            }
        },
        {
            "name": "telegram_pin_chat_message",
            "description": "Закрепить сообщение в чате",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "chat_id": {
                        "type": "string",
                        "description": "ID чата"
                    },
                    "message_id": {
                        "type": "integer",
                        "description": "ID сообщения"
                    }
                },
                "required": ["chat_id", "message_id"]
            }
        },
        {
            "name": "telegram_unpin_chat_message",
            "description": "Открепить сообщение в чате",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "chat_id": {
                        "type": "string",
                        "description": "ID чата"
                    }
                },
                "required": ["chat_id"]
            }
        },
        {
            "name": "telegram_unpin_all_chat_messages",
            "description": "Открепить все сообщения в чате",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "chat_id": {
                        "type": "string",
                        "description": "ID чата"
                    }
                },
                "required": ["chat_id"]
            }
        },
        {
            "name": "telegram_leave_chat",
            "description": "Покинуть чат",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "chat_id": {
                        "type": "string",
                        "description": "ID чата"
                    }
                },
                "required": ["chat_id"]
            }
        },
        {
            "name": "telegram_answer_callback_query",
            "description": "Ответить на callback query",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "callback_query_id": {
                        "type": "string",
                        "description": "ID callback query"
                    },
                    "text": {
                        "type": "string",
                        "description": "Текст ответа"
                    }
                },
                "required": ["callback_query_id"]
            }
        },
        {
            "name": "telegram_answer_inline_query",
            "description": "Ответить на inline query",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "inline_query_id": {
                        "type": "string",
                        "description": "ID inline query"
                    },
                    "results": {
                        "type": "array",
                        "description": "Результаты inline query"
                    }
                },
                "required": ["inline_query_id", "results"]
            }
        },
        {
            "name": "telegram_stop_poll",
            "description": "Остановить опрос",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "chat_id": {
                        "type": "string",
                        "description": "ID чата"
                    },
                    "message_id": {
                        "type": "integer",
                        "description": "ID сообщения с опросом"
                    }
                },
                "required": ["chat_id", "message_id"]
            }
        },
        {
            "name": "telegram_send_poll",
            "description": "Отправить опрос",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "chat_id": {
                        "type": "string",
                        "description": "ID чата"
                    },
                    "question": {
                        "type": "string",
                        "description": "Вопрос опроса"
                    },
                    "options": {
                        "type": "array",
                        "description": "Варианты ответов"
                    }
                },
                "required": ["chat_id", "question", "options"]
            }
        },
        {
            "name": "telegram_send_dice",
            "description": "Отправить кубик",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "chat_id": {
                        "type": "string",
                        "description": "ID чата"
                    }
                },
                "required": ["chat_id"]
            }
        },
        {
            "name": "telegram_send_game",
            "description": "Отправить игру",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "chat_id": {
                        "type": "string",
                        "description": "ID чата"
                    },
                    "game_short_name": {
                        "type": "string",
                        "description": "Короткое имя игры"
                    }
                },
                "required": ["chat_id", "game_short_name"]
            }
        },
        {
            "name": "telegram_send_invoice",
            "description": "Отправить счёт",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "chat_id": {
                        "type": "string",
                        "description": "ID чата"
                    },
                    "title": {
                        "type": "string",
                        "description": "Название товара"
                    },
                    "description": {
                        "type": "string",
                        "description": "Описание товара"
                    },
                    "payload": {
                        "type": "string",
                        "description": "Данные счёта"
                    },
                    "provider_token": {
                        "type": "string",
                        "description": "Токен провайдера"
                    },
                    "currency": {
                        "type": "string",
                        "description": "Валюта"
                    },
                    "prices": {
                        "type": "array",
                        "description": "Цены"
                    }
                },
                "required": ["chat_id", "title", "description", "payload", "provider_token", "currency", "prices"]
            }
        },
        {
            "name": "telegram_send_media_group",
            "description": "Отправить группу медиа",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "chat_id": {
                        "type": "string",
                        "description": "ID чата"
                    },
                    "media": {
                        "type": "array",
                        "description": "Список медиа"
                    }
                },
                "required": ["chat_id", "media"]
            }
        },
        {
            "name": "telegram_send_animation",
            "description": "Отправить анимацию (GIF)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "chat_id": {
                        "type": "string",
                        "description": "ID чата"
                    },
                    "animation": {
                        "type": "string",
                        "description": "URL анимации или file_id"
                    },
                    "caption": {
                        "type": "string",
                        "description": "Подпись"
                    }
                },
                "required": ["chat_id", "animation"]
            }
        },
        {
            "name": "telegram_send_audio",
            "description": "Отправить аудио",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "chat_id": {
                        "type": "string",
                        "description": "ID чата"
                    },
                    "audio": {
                        "type": "string",
                        "description": "URL аудио или file_id"
                    },
                    "caption": {
                        "type": "string",
                        "description": "Подпись"
                    }
                },
                "required": ["chat_id", "audio"]
            }
        },
        {
            "name": "telegram_send_video",
            "description": "Отправить видео",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "chat_id": {
                        "type": "string",
                        "description": "ID чата"
                    },
                    "video": {
                        "type": "string",
                        "description": "URL видео или file_id"
                    },
                    "caption": {
                        "type": "string",
                        "description": "Подпись"
                    }
                },
                "required": ["chat_id", "video"]
            }
        },
        {
            "name": "telegram_send_video_note",
            "description": "Отправить видеосообщение",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "chat_id": {
                        "type": "string",
                        "description": "ID чата"
                    },
                    "video_note": {
                        "type": "string",
                        "description": "URL видеосообщения или file_id"
                    }
                },
                "required": ["chat_id", "video_note"]
            }
        },
        {
            "name": "telegram_send_voice",
            "description": "Отправить голосовое сообщение",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "chat_id": {
                        "type": "string",
                        "description": "ID чата"
                    },
                    "voice": {
                        "type": "string",
                        "description": "URL голосового сообщения или file_id"
                    },
                    "caption": {
                        "type": "string",
                        "description": "Подпись"
                    }
                },
                "required": ["chat_id", "voice"]
            }
        },
        {
            "name": "telegram_send_sticker",
            "description": "Отправить стикер",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "chat_id": {
                        "type": "string",
                        "description": "ID чата"
                    },
                    "sticker": {
                        "type": "string",
                        "description": "URL стикера или file_id"
                    }
                },
                "required": ["chat_id", "sticker"]
            }
        },
        {
            "name": "telegram_get_sticker_set",
            "description": "Получить набор стикеров",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Название набора стикеров"
                    }
                },
                "required": ["name"]
            }
        },
        {
            "name": "telegram_upload_sticker_file",
            "description": "Загрузить файл стикера",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "integer",
                        "description": "ID пользователя"
                    },
                    "png_sticker": {
                        "type": "string",
                        "description": "URL PNG стикера"
                    }
                },
                "required": ["user_id", "png_sticker"]
            }
        },
        {
            "name": "telegram_create_new_sticker_set",
            "description": "Создать новый набор стикеров",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "integer",
                        "description": "ID пользователя"
                    },
                    "name": {
                        "type": "string",
                        "description": "Название набора"
                    },
                    "title": {
                        "type": "string",
                        "description": "Заголовок набора"
                    },
                    "png_sticker": {
                        "type": "string",
                        "description": "URL PNG стикера"
                    },
                    "emojis": {
                        "type": "string",
                        "description": "Эмодзи для стикера"
                    }
                },
                "required": ["user_id", "name", "title", "png_sticker", "emojis"]
            }
        },
        {
            "name": "telegram_add_sticker_to_set",
            "description": "Добавить стикер в набор",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "integer",
                        "description": "ID пользователя"
                    },
                    "name": {
                        "type": "string",
                        "description": "Название набора"
                    },
                    "png_sticker": {
                        "type": "string",
                        "description": "URL PNG стикера"
                    },
                    "emojis": {
                        "type": "string",
                        "description": "Эмодзи для стикера"
                    }
                },
                "required": ["user_id", "name", "png_sticker", "emojis"]
            }
        },
        {
            "name": "telegram_set_sticker_position_in_set",
            "description": "Установить позицию стикера в наборе",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "sticker": {
                        "type": "string",
                        "description": "ID стикера"
                    },
                    "position": {
                        "type": "integer",
                        "description": "Новая позиция"
                    }
                },
                "required": ["sticker", "position"]
            }
        },
        {
            "name": "telegram_delete_sticker_from_set",
            "description": "Удалить стикер из набора",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "sticker": {
                        "type": "string",
                        "description": "ID стикера"
                    }
                },
                "required": ["sticker"]
            }
        },
        {
            "name": "telegram_set_sticker_set_thumb",
            "description": "Установить миниатюру набора стикеров",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Название набора"
                    },
                    "user_id": {
                        "type": "integer",
                        "description": "ID пользователя"
                    },
                    "thumb": {
                        "type": "string",
                        "description": "URL миниатюры"
                    }
                },
                "required": ["name", "user_id", "thumb"]
            }
        },
        {
            "name": "telegram_send_chat_action",
            "description": "Отправить действие чата",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "chat_id": {
                        "type": "string",
                        "description": "ID чата"
                    },
                    "action": {
                        "type": "string",
                        "description": "Тип действия"
                    }
                },
                "required": ["chat_id", "action"]
            }
        },
        {
            "name": "telegram_get_user_profile_photos",
            "description": "Получить фото профиля пользователя",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "integer",
                        "description": "ID пользователя"
                    },
                    "offset": {
                        "type": "integer",
                        "description": "Смещение"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Лимит"
                    }
                },
                "required": ["user_id"]
            }
        },
        {
            "name": "telegram_get_file",
            "description": "Получить файл",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "file_id": {
                        "type": "string",
                        "description": "ID файла"
                    }
                },
                "required": ["file_id"]
            }
        },
        {
            "name": "telegram_kick_chat_member",
            "description": "Исключить участника из чата",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "chat_id": {
                        "type": "string",
                        "description": "ID чата"
                    },
                    "user_id": {
                        "type": "integer",
                        "description": "ID пользователя"
                    }
                },
                "required": ["chat_id", "user_id"]
            }
        },
        {
            "name": "telegram_set_chat_administrator_custom_title",
            "description": "Установить кастомный титул администратора",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "chat_id": {
                        "type": "string",
                        "description": "ID чата"
                    },
                    "user_id": {
                        "type": "integer",
                        "description": "ID пользователя"
                    },
                    "custom_title": {
                        "type": "string",
                        "description": "Кастомный титул"
                    }
                },
                "required": ["chat_id", "user_id", "custom_title"]
            }
        },
        {
            "name": "telegram_ban_chat_sender_chat",
            "description": "Заблокировать отправителя чата",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "chat_id": {
                        "type": "string",
                        "description": "ID чата"
                    },
                    "sender_chat_id": {
                        "type": "integer",
                        "description": "ID отправителя"
                    }
                },
                "required": ["chat_id", "sender_chat_id"]
            }
        },
        {
            "name": "telegram_unban_chat_sender_chat",
            "description": "Разблокировать отправителя чата",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "chat_id": {
                        "type": "string",
                        "description": "ID чата"
                    },
                    "sender_chat_id": {
                        "type": "integer",
                        "description": "ID отправителя"
                    }
                },
                "required": ["chat_id", "sender_chat_id"]
            }
        },
        {
            "name": "telegram_set_chat_permissions",
            "description": "Установить права чата",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "chat_id": {
                        "type": "string",
                        "description": "ID чата"
                    },
                    "permissions": {
                        "type": "object",
                        "description": "Права чата"
                    }
                },
                "required": ["chat_id", "permissions"]
            }
        },
        {
            "name": "telegram_edit_chat_invite_link",
            "description": "Редактировать ссылку-приглашение",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "chat_id": {
                        "type": "string",
                        "description": "ID чата"
                    },
                    "invite_link": {
                        "type": "string",
                        "description": "Ссылка-приглашение"
                    },
                    "expire_date": {
                        "type": "integer",
                        "description": "Дата истечения"
                    },
                    "member_limit": {
                        "type": "integer",
                        "description": "Лимит участников"
                    }
                },
                "required": ["chat_id", "invite_link"]
            }
        },
        {
            "name": "telegram_set_chat_sticker_set",
            "description": "Установить набор стикеров чата",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "chat_id": {
                        "type": "string",
                        "description": "ID чата"
                    },
                    "sticker_set_name": {
                        "type": "string",
                        "description": "Название набора стикеров"
                    }
                },
                "required": ["chat_id", "sticker_set_name"]
            }
        },
        {
            "name": "telegram_delete_chat_sticker_set",
            "description": "Удалить набор стикеров чата",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "chat_id": {
                        "type": "string",
                        "description": "ID чата"
                    }
                },
                "required": ["chat_id"]
            }
        }
    ]


def get_all_mcp_tools() -> list:
    """
    Получить полный список всех MCP tools
    
    Returns:
        Объединённый список WordPress + Wordstat + Telegram tools
    """
    return get_wordpress_tools() + get_wordstat_tools() + get_telegram_tools()


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

