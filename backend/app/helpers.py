"""
Helper Functions
Вспомогательные функции для валидации, санитизации и утилиты
"""
import re
import secrets
import string
from typing import Optional, Dict, Any
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)


# ==================== URL VALIDATION ====================

def is_valid_url(url: str) -> bool:
    """
    Проверка валидности URL
    
    Args:
        url: URL для проверки
    
    Returns:
        True если URL валиден, False иначе
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc]) and result.scheme in ['http', 'https']
    except Exception:
        return False


def sanitize_url(url: str) -> str:
    """
    Санитизация URL (удаление trailing slash, приведение к lowercase для схемы/хоста)
    
    Args:
        url: URL для санитизации
    
    Returns:
        Санитизированный URL
    """
    if not url:
        return url
    
    try:
        parsed = urlparse(url)
        # Приводим схему и netloc к lowercase, оставляем path как есть
        scheme = parsed.scheme.lower()
        netloc = parsed.netloc.lower()
        path = parsed.path.rstrip('/')  # Убираем trailing slash
        
        sanitized = f"{scheme}://{netloc}{path}"
        
        # Добавляем query и fragment если есть
        if parsed.query:
            sanitized += f"?{parsed.query}"
        if parsed.fragment:
            sanitized += f"#{parsed.fragment}"
        
        return sanitized
    except Exception as e:
        logger.warning(f"Failed to sanitize URL '{url}': {str(e)}")
        return url.rstrip('/')


# ==================== STRING VALIDATION ====================

def is_valid_email(email: str) -> bool:
    """
    Базовая проверка email
    
    Args:
        email: Email для проверки
    
    Returns:
        True если email валиден, False иначе
    """
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def sanitize_string(text: str, max_length: Optional[int] = None) -> str:
    """
    Санитизация строки (удаление опасных символов, обрезка)
    
    Args:
        text: Текст для санитизации
        max_length: Максимальная длина (None = без ограничения)
    
    Returns:
        Санитизированная строка
    """
    if not text:
        return ""
    
    # Удаляем control characters (кроме \n, \r, \t)
    sanitized = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    
    # Обрезаем если задана максимальная длина
    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized.strip()


# ==================== TOKEN GENERATION ====================

def generate_token(length: int = 32) -> str:
    """
    Генерация безопасного случайного токена
    
    Args:
        length: Длина токена (по умолчанию 32)
    
    Returns:
        Hex-строка токена
    """
    return secrets.token_hex(length)


def generate_connector_id() -> str:
    """
    Генерация уникального ID коннектора
    
    Returns:
        Строка формата conn_XXXXXXXXXXXXX
    """
    random_part = ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(16))
    return f"conn_{random_part}"


# ==================== DATA VALIDATION ====================

def validate_dict_keys(data: Dict[str, Any], required_keys: list, optional_keys: Optional[list] = None) -> tuple[bool, str]:
    """
    Валидация ключей словаря
    
    Args:
        data: Словарь для проверки
        required_keys: Список обязательных ключей
        optional_keys: Список опциональных ключей (если указан, проверяется отсутствие лишних ключей)
    
    Returns:
        Tuple (is_valid, error_message)
    """
    if not isinstance(data, dict):
        return False, "Data must be a dictionary"
    
    # Проверяем наличие обязательных ключей
    missing_keys = [key for key in required_keys if key not in data]
    if missing_keys:
        return False, f"Missing required keys: {', '.join(missing_keys)}"
    
    # Если указаны optional_keys, проверяем что нет лишних ключей
    if optional_keys is not None:
        allowed_keys = set(required_keys + optional_keys)
        extra_keys = set(data.keys()) - allowed_keys
        if extra_keys:
            return False, f"Unexpected keys: {', '.join(extra_keys)}"
    
    return True, ""


def validate_integer(value: Any, min_value: Optional[int] = None, max_value: Optional[int] = None) -> tuple[bool, str]:
    """
    Валидация целочисленного значения
    
    Args:
        value: Значение для проверки
        min_value: Минимальное значение (включительно)
        max_value: Максимальное значение (включительно)
    
    Returns:
        Tuple (is_valid, error_message)
    """
    try:
        int_value = int(value)
        
        if min_value is not None and int_value < min_value:
            return False, f"Value must be >= {min_value}"
        
        if max_value is not None and int_value > max_value:
            return False, f"Value must be <= {max_value}"
        
        return True, ""
    
    except (ValueError, TypeError):
        return False, "Value must be an integer"


# ==================== JSON-RPC HELPERS ====================

def create_jsonrpc_response(request_id: Any, result: Any) -> Dict[str, Any]:
    """
    Создание успешного JSON-RPC ответа
    
    Args:
        request_id: ID запроса
        result: Результат выполнения
    
    Returns:
        JSON-RPC response dict
    """
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": result
    }


def create_jsonrpc_error(request_id: Any, code: int, message: str, data: Optional[Any] = None) -> Dict[str, Any]:
    """
    Создание JSON-RPC ответа с ошибкой
    
    Args:
        request_id: ID запроса
        code: Код ошибки
        message: Сообщение об ошибке
        data: Дополнительные данные (опционально)
    
    Returns:
        JSON-RPC error response dict
    """
    error = {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {
            "code": code,
            "message": message
        }
    }
    
    if data is not None:
        error["error"]["data"] = data
    
    return error


# Стандартные коды ошибок JSON-RPC
class JSONRPCErrorCodes:
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603
    SERVER_ERROR = -32000


# ==================== MCP RESPONSE HELPERS ====================

def create_mcp_text_response(text: str) -> Dict[str, Any]:
    """
    Создание MCP response с текстовым содержимым
    
    Args:
        text: Текстовое содержимое ответа
    
    Returns:
        MCP response content dict
    """
    return {
        "content": [
            {
                "type": "text",
                "text": text
            }
        ]
    }


def create_mcp_tool_result(request_id: Any, text: str) -> Dict[str, Any]:
    """
    Создание полного MCP tool result response
    
    Args:
        request_id: ID запроса
        text: Текстовое содержимое результата
    
    Returns:
        Полный JSON-RPC + MCP response
    """
    return create_jsonrpc_response(request_id, create_mcp_text_response(text))


# ==================== SAFE OPERATIONS ====================

def safe_get(dictionary: Dict, *keys, default=None):
    """
    Безопасное получение вложенного значения из словаря
    
    Args:
        dictionary: Словарь для поиска
        *keys: Последовательность ключей для вложенного доступа
        default: Значение по умолчанию если ключ не найден
    
    Returns:
        Значение или default
    
    Example:
        safe_get(data, "user", "profile", "name", default="Unknown")
    """
    result = dictionary
    
    for key in keys:
        if isinstance(result, dict) and key in result:
            result = result[key]
        else:
            return default
    
    return result


def safe_int(value: Any, default: int = 0) -> int:
    """
    Безопасное преобразование в int
    
    Args:
        value: Значение для преобразования
        default: Значение по умолчанию если преобразование невозможно
    
    Returns:
        int значение или default
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_str(value: Any, default: str = "") -> str:
    """
    Безопасное преобразование в str
    
    Args:
        value: Значение для преобразования
        default: Значение по умолчанию если value is None
    
    Returns:
        str значение или default
    """
    if value is None:
        return default
    return str(value)


# ==================== LOGGING HELPERS ====================

def mask_sensitive_data(data: str, visible_chars: int = 4) -> str:
    """
    Маскирование чувствительных данных (токены, пароли и т.д.)
    
    Args:
        data: Данные для маскирования
        visible_chars: Количество видимых символов в начале и конце
    
    Returns:
        Замаскированная строка
    
    Example:
        mask_sensitive_data("my_secret_token_12345") -> "my_s***12345"
    """
    if not data or len(data) <= visible_chars * 2:
        return "***"
    
    return f"{data[:visible_chars]}***{data[-visible_chars:]}"


def log_api_call(service: str, endpoint: str, status: int, duration_ms: Optional[float] = None):
    """
    Логирование API вызова
    
    Args:
        service: Название сервиса (WordPress, Wordstat, etc.)
        endpoint: API endpoint
        status: HTTP status code
        duration_ms: Длительность запроса в миллисекундах
    """
    duration_str = f" ({duration_ms:.2f}ms)" if duration_ms else ""
    logger.info(f"[{service}] {endpoint} -> {status}{duration_str}")


# ==================== RATE LIMITING HELPERS ====================

class SimpleRateLimiter:
    """
    Простой rate limiter на основе временных окон
    """
    
    def __init__(self, max_requests: int, window_seconds: int):
        """
        Args:
            max_requests: Максимальное количество запросов
            window_seconds: Размер временного окна в секундах
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, list] = {}
    
    def is_allowed(self, key: str) -> bool:
        """
        Проверка, разрешён ли запрос
        
        Args:
            key: Идентификатор клиента (user_id, IP, etc.)
        
        Returns:
            True если запрос разрешён, False иначе
        """
        import time
        
        now = time.time()
        
        # Инициализируем список запросов для ключа если его нет
        if key not in self.requests:
            self.requests[key] = []
        
        # Очищаем старые запросы за пределами окна
        self.requests[key] = [req_time for req_time in self.requests[key] 
                              if now - req_time < self.window_seconds]
        
        # Проверяем лимит
        if len(self.requests[key]) >= self.max_requests:
            return False
        
        # Добавляем текущий запрос
        self.requests[key].append(now)
        return True
    
    def reset(self, key: str):
        """
        Сброс счётчика для ключа
        
        Args:
            key: Идентификатор клиента
        """
        if key in self.requests:
            del self.requests[key]

