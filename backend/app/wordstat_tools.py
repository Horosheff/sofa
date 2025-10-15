"""
Yandex Wordstat MCP Tools
Все инструменты для работы с Yandex Wordstat API
"""
import httpx
import json
from typing import Optional, Dict, Any, List
from .models import UserSettings
from .helpers import log_api_call, safe_get
import logging
import time

logger = logging.getLogger(__name__)

# Константы Wordstat API
WORDSTAT_API_BASE = "https://api.wordstat.yandex.net/v1"
WORDSTAT_OAUTH_URL = "https://oauth.yandex.ru"


async def validate_wordstat_settings(settings: UserSettings, check_token: bool = True) -> tuple[bool, str]:
    """Валидация настроек Wordstat"""
    if check_token and not settings.wordstat_access_token:
        return False, "Токен Wordstat не настроен"
    return True, ""


async def wordstat_api_call(
    endpoint: str,
    settings: UserSettings,
    json_data: Optional[Dict[str, Any]] = None,
    timeout: int = 30
) -> Dict[str, Any]:
    """
    Универсальный метод для вызова Yandex Wordstat API
    
    Args:
        endpoint: Endpoint API (например, /userInfo)
        settings: Настройки пользователя
        json_data: JSON данные для POST
        timeout: Таймаут запроса
    
    Returns:
        Dict с результатом или raises Exception
    """
    full_url = f"{WORDSTAT_API_BASE}{endpoint}"
    start_time = time.time()
    
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                full_url,
                headers={
                    "Authorization": f"Bearer {settings.wordstat_access_token}",
                    "Content-Type": "application/json;charset=utf-8"
                },
                json=json_data or {},
                timeout=timeout
            )
            
            duration_ms = (time.time() - start_time) * 1000
            log_api_call("Wordstat", endpoint, resp.status_code, duration_ms)
            
            logger.info(f"Wordstat API {endpoint} response: {resp.text[:500]}")
            
            resp.raise_for_status()
            return resp.json()
            
    except httpx.HTTPStatusError as e:
        logger.error(f"Wordstat API HTTP error: {e.response.status_code} - {e.response.text}")
        raise Exception(f"Wordstat API ошибка {e.response.status_code}: {e.response.text[:200]}")
    except httpx.RequestError as e:
        logger.error(f"Wordstat API request error: {str(e)}")
        raise Exception(f"Ошибка соединения с Wordstat: {str(e)}")
    except Exception as e:
        logger.error(f"Wordstat API unexpected error: {str(e)}")
        raise


# ==================== USER INFO ====================

async def wordstat_get_user_info(settings: UserSettings, tool_args: Dict[str, Any]) -> str:
    """Получить информацию о пользователе Wordstat"""
    
    # Проверка базовых настроек
    if not settings.wordstat_access_token and not settings.wordstat_client_id:
        return """❌ Wordstat не настроен!

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
    
    if not settings.wordstat_access_token and settings.wordstat_client_id:
        return f"""⚠️ Wordstat настроен частично!

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
    
    # Есть токен - проверяем через API
    try:
        data = await wordstat_api_call("/userInfo", settings)
        
        if "userInfo" in data:
            user_info = data["userInfo"]
            return f"""✅ Подключение к Wordstat успешно!

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
            return f"""⚠️ Необычный ответ от API:
{json.dumps(data, indent=2, ensure_ascii=False)}"""
    
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg:
            return f"""❌ Токен недействителен (401 Unauthorized)

🔧 Причины:
1. Токен устарел или неправильный
2. Токен был получен для другого приложения
3. У аккаунта нет доступа к Wordstat API

📋 Что делать:
1. Получите новый токен через: 
   https://oauth.yandex.ru/authorize?response_type=token&client_id={settings.wordstat_client_id or 'c654b948515a4a07a4c89648a0831d40'}

2. Убедитесь, что:
   - Авторизуетесь под правильным аккаунтом Яндекса
   - У аккаунта есть доступ к Wordstat
   - Client ID правильный"""
        
        return f"""❌ Ошибка при подключении к Wordstat API:
{error_msg}

Проверьте интернет-соединение или попробуйте позже."""


# ==================== REGIONS ====================

async def wordstat_get_regions_tree(settings: UserSettings, tool_args: Dict[str, Any]) -> str:
    """Получить дерево регионов"""
    is_valid, error_msg = await validate_wordstat_settings(settings)
    if not is_valid:
        return f"❌ {error_msg}"
    
    try:
        data = await wordstat_api_call("/getRegionsTree", settings)
        
        # API возвращает список напрямую (не объект с ключом 'regions')
        if isinstance(data, list):
            regions_list = data
        elif isinstance(data, dict) and 'regions' in data:
            regions_list = data['regions']
        else:
            return f"❌ Неожиданный формат ответа API. Тип: {type(data)}"
        
        result = "✅ Дерево регионов Yandex Wordstat:\n\n"
        
        def format_regions(regions, level=0):
            text = ""
            if not isinstance(regions, list):
                return "⚠️ Ожидался список регионов\n"
            
            for region in regions[:20] if level == 0 else regions:
                if not isinstance(region, dict):
                    continue
                
                indent = "  " * level
                region_id = region.get('value') or region.get('id', 'N/A')
                region_name = region.get('label') or region.get('name', 'N/A')
                text += f"{indent}• {region_name} (ID: {region_id})\n"
                
                children = region.get('children')
                if children and isinstance(children, list):
                    text += format_regions(children, level + 1)
            
            return text
        
        result += format_regions(regions_list)
        result += "\n💡 Используйте ID регионов для других запросов"
        
        return result
    
    except Exception as e:
        logger.error(f"Wordstat /v1/getRegionsTree exception: {str(e)}", exc_info=True)
        return f"❌ Ошибка: {str(e)}"


# ==================== TOP REQUESTS ====================

async def wordstat_get_top_requests(settings: UserSettings, tool_args: Dict[str, Any]) -> str:
    """Получить топ запросов по ключевому слову"""
    phrase = tool_args.get("phrase")
    
    if not phrase:
        return "❌ Ошибка: не указана фраза для поиска (параметр 'phrase')"
    
    is_valid, error_msg = await validate_wordstat_settings(settings)
    if not is_valid:
        return f"❌ {error_msg}"
    
    num_phrases = tool_args.get("numPhrases", 50)
    regions = tool_args.get("regions", [225])  # По умолчанию Россия
    devices = tool_args.get("devices", ["all"])
    
    try:
        data = await wordstat_api_call(
            "/topRequests",
            settings,
            json_data={
                "phrase": phrase,
                "numPhrases": num_phrases,
                "regions": regions,
                "devices": devices
            }
        )
        
        if isinstance(data, dict) and 'topRequests' in data:
            requests_list = data['topRequests']
            
            if not requests_list:
                return f"Нет данных по запросу '{phrase}'"
            
            result = f"✅ Топ запросов по ключевому слову '{phrase}':\n\n"
            for idx, req in enumerate(requests_list[:20], 1):
                phrase_text = req.get('phrase', 'N/A')
                shows = req.get('shows', 'N/A')
                result += f"{idx}. {phrase_text} - показов: {shows}\n"
            
            if len(requests_list) > 20:
                result += f"\n... и ещё {len(requests_list) - 20} запросов"
            
            return result
        else:
            return f"❌ Неожиданный формат ответа: {json.dumps(data, indent=2, ensure_ascii=False)[:300]}"
    
    except Exception as e:
        return f"❌ Ошибка: {str(e)}"


# ==================== DYNAMICS ====================

async def wordstat_get_dynamics(settings: UserSettings, tool_args: Dict[str, Any]) -> str:
    """Получить динамику запросов"""
    phrase = tool_args.get("phrase")
    
    if not phrase:
        return "❌ Ошибка: не указана фраза для анализа (параметр 'phrase')"
    
    is_valid, error_msg = await validate_wordstat_settings(settings)
    if not is_valid:
        return f"❌ {error_msg}"
    
    regions = tool_args.get("regions", [225])
    devices = tool_args.get("devices", ["all"])
    
    try:
        data = await wordstat_api_call(
            "/dynamics",
            settings,
            json_data={
                "phrase": phrase,
                "regions": regions,
                "devices": devices
            }
        )
        
        if isinstance(data, dict) and 'dynamics' in data:
            dynamics_data = data['dynamics']
            
            if not dynamics_data:
                return f"Нет данных по динамике для '{phrase}'"
            
            result = f"✅ Динамика запроса '{phrase}':\n\n"
            for entry in dynamics_data:
                period = entry.get('period', 'N/A')
                shows = entry.get('shows', 'N/A')
                result += f"{period}: {shows} показов\n"
            
            return result
        else:
            return f"❌ Неожиданный формат ответа: {json.dumps(data, indent=2, ensure_ascii=False)[:300]}"
    
    except Exception as e:
        return f"❌ Ошибка: {str(e)}"


# ==================== REGIONS STATS ====================

async def wordstat_get_regions(settings: UserSettings, tool_args: Dict[str, Any]) -> str:
    """Получить статистику по регионам"""
    phrase = tool_args.get("phrase")
    
    if not phrase:
        return "❌ Ошибка: не указана фраза для анализа (параметр 'phrase')"
    
    is_valid, error_msg = await validate_wordstat_settings(settings)
    if not is_valid:
        return f"❌ {error_msg}"
    
    regions = tool_args.get("regions", [225])
    devices = tool_args.get("devices", ["all"])
    
    try:
        data = await wordstat_api_call(
            "/regions",
            settings,
            json_data={
                "phrase": phrase,
                "regions": regions,
                "devices": devices
            }
        )
        
        if isinstance(data, dict) and 'regions' in data:
            regions_data = data['regions']
            
            if not regions_data:
                return f"Нет данных по регионам для '{phrase}'"
            
            result = f"✅ Статистика по регионам для '{phrase}':\n\n"
            for entry in regions_data[:20]:
                region_id = entry.get('regionId', 'N/A')
                region_name = entry.get('regionName', 'N/A')
                shows = entry.get('shows', 'N/A')
                result += f"{region_name} (ID: {region_id}): {shows} показов\n"
            
            if len(regions_data) > 20:
                result += f"\n... и ещё {len(regions_data) - 20} регионов"
            
            return result
        else:
            return f"❌ Неожиданный формат ответа: {json.dumps(data, indent=2, ensure_ascii=False)[:300]}"
    
    except Exception as e:
        return f"❌ Ошибка: {str(e)}"


# ==================== SET TOKEN ====================

async def wordstat_set_token(settings: UserSettings, tool_args: Dict[str, Any], db) -> str:
    """Установить токен Wordstat"""
    from .database import SessionLocal
    
    token = tool_args.get("token")
    
    if not token:
        return "❌ Ошибка: не указан токен (параметр 'token')"
    
    # Сохраняем токен в базу
    settings.wordstat_access_token = token
    db.commit()
    
    return f"""✅ Токен Wordstat успешно сохранён!

Теперь проверьте подключение:
• wordstat_get_user_info - информация об аккаунте

Используйте инструменты:
• wordstat_get_top_requests - топ запросов по ключевому слову
• wordstat_get_regions_tree - список регионов
• wordstat_get_dynamics - динамика запросов
• wordstat_get_regions - статистика по регионам"""


# ==================== AUTO SETUP ====================

async def wordstat_auto_setup(settings: UserSettings, tool_args: Dict[str, Any]) -> str:
    """Автоматическая настройка Wordstat с инструкциями"""
    
    status_lines = [
        "🔧 Статус настройки Yandex Wordstat:",
        "",
    ]
    
    # Проверяем Client ID
    if settings.wordstat_client_id:
        status_lines.append(f"✅ Client ID настроен: {settings.wordstat_client_id}")
    else:
        status_lines.append("❌ Client ID не настроен")
        status_lines.append("")
        status_lines.append("📋 Как получить Client ID:")
        status_lines.append("1. Перейдите на https://oauth.yandex.ru")
        status_lines.append("2. Зарегистрируйте новое приложение")
        status_lines.append("3. Скопируйте Client ID из настроек приложения")
        status_lines.append("4. Сохраните его в разделе 'Настройки' на dashboard")
    
    status_lines.append("")
    
    # Проверяем Client Secret
    if settings.wordstat_client_secret:
        status_lines.append("✅ Client Secret настроен")
    else:
        status_lines.append("❌ Client Secret не настроен")
    
    status_lines.append("")
    
    # Проверяем Access Token
    if settings.wordstat_access_token:
        status_lines.append("✅ Access Token настроен")
        status_lines.append("")
        status_lines.append("🎉 Wordstat полностью настроен!")
        status_lines.append("")
        status_lines.append("Проверьте подключение: wordstat_get_user_info")
    else:
        status_lines.append("❌ Access Token не настроен")
        
        if settings.wordstat_client_id:
            status_lines.append("")
            status_lines.append("🔐 Для получения Access Token:")
            status_lines.append(f"1. Откройте: https://oauth.yandex.ru/authorize?response_type=token&client_id={settings.wordstat_client_id}")
            status_lines.append("2. Разрешите доступ к приложению")
            status_lines.append("3. Скопируйте access_token из URL")
            status_lines.append("4. Используйте wordstat_set_token для сохранения")
        else:
            status_lines.append("")
            status_lines.append("⚠️ Сначала настройте Client ID и Client Secret в разделе 'Настройки'")
    
    status_lines.append("")
    status_lines.append("📚 Доступные инструменты после настройки:")
    status_lines.append("")
    status_lines.append("Используйте инструменты:")
    status_lines.append("• wordstat_get_top_requests - топ запросов по ключевому слову")
    status_lines.append("• wordstat_get_regions_tree - список регионов")
    status_lines.append("• wordstat_get_dynamics - динамика запросов")
    status_lines.append("• wordstat_get_regions - статистика по регионам")
    status_lines.append("")
    status_lines.append("Проверьте подключение: wordstat_get_user_info")
    
    return "\n".join(status_lines)


# ==================== TOOL ROUTER ====================

async def handle_wordstat_tool(tool_name: str, settings: UserSettings, tool_args: Dict[str, Any], db) -> str:
    """
    Роутер для всех Wordstat инструментов
    
    Args:
        tool_name: Название инструмента
        settings: Настройки пользователя
        tool_args: Аргументы инструмента
        db: Database session (для set_token)
    
    Returns:
        Результат выполнения в виде строки
    """
    tools_map = {
        "wordstat_get_user_info": wordstat_get_user_info,
        "wordstat_get_regions_tree": wordstat_get_regions_tree,
        "wordstat_get_top_requests": wordstat_get_top_requests,
        "wordstat_get_dynamics": wordstat_get_dynamics,
        "wordstat_get_regions": wordstat_get_regions,
        "wordstat_auto_setup": wordstat_auto_setup,
    }
    
    # Специальные handlers, требующие db session
    if tool_name == "wordstat_set_token":
        return await wordstat_set_token(settings, tool_args, db)
    
    handler = tools_map.get(tool_name)
    if not handler:
        return f"❌ Неизвестный Wordstat инструмент: {tool_name}"
    
    try:
        return await handler(settings, tool_args)
    except Exception as e:
        logger.error(f"Wordstat tool {tool_name} error: {str(e)}")
        return f"❌ Ошибка выполнения {tool_name}: {str(e)}"

