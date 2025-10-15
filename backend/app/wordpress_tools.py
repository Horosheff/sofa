"""
WordPress MCP Tools
Все инструменты для работы с WordPress REST API
"""
import httpx
from typing import Optional, Dict, Any, List
from .models import UserSettings
from .helpers import sanitize_url, is_valid_url, log_api_call
import logging
import time

logger = logging.getLogger(__name__)


async def validate_wordpress_settings(settings: UserSettings) -> tuple[bool, str]:
    """Валидация настроек WordPress"""
    if not settings.wordpress_url:
        return False, "WordPress URL не настроен"
    
    if not is_valid_url(settings.wordpress_url):
        return False, "WordPress URL невалиден (должен начинаться с http:// или https://)"
    
    if not settings.wordpress_username:
        return False, "WordPress username не настроен"
    if not settings.wordpress_password:
        return False, "WordPress password не настроен"
    return True, ""


async def wordpress_api_call(
    method: str,
    endpoint: str,
    settings: UserSettings,
    json_data: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None,
    files: Optional[Dict[str, Any]] = None,
    timeout: int = 30
) -> Dict[str, Any]:
    """
    Универсальный метод для вызова WordPress REST API
    
    Args:
        method: HTTP метод (GET, POST, DELETE)
        endpoint: Endpoint API (например, /wp/v2/posts)
        settings: Настройки пользователя
        json_data: JSON данные для POST/PUT
        params: Query параметры
        files: Файлы для загрузки
        timeout: Таймаут запроса
    
    Returns:
        Dict с результатом или raises Exception
    """
    wp_url = sanitize_url(settings.wordpress_url)
    wp_user = settings.wordpress_username
    wp_pass = settings.wordpress_password
    
    full_url = f"{wp_url}{endpoint}"
    
    start_time = time.time()
    
    try:
        async with httpx.AsyncClient() as client:
            auth = (wp_user, wp_pass) if wp_user and wp_pass else None
            
            if method == "GET":
                resp = await client.get(full_url, params=params, auth=auth, timeout=timeout)
            elif method == "POST":
                if files:
                    resp = await client.post(full_url, files=files, auth=auth, timeout=timeout)
                else:
                    resp = await client.post(full_url, json=json_data, auth=auth, timeout=timeout)
            elif method == "DELETE":
                resp = await client.delete(full_url, params=params, auth=auth, timeout=timeout)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            duration_ms = (time.time() - start_time) * 1000
            log_api_call("WordPress", endpoint, resp.status_code, duration_ms)
            
            resp.raise_for_status()
            return resp.json()
            
    except httpx.HTTPStatusError as e:
        logger.error(f"WordPress API HTTP error: {e.response.status_code} - {e.response.text}")
        raise Exception(f"WordPress API ошибка {e.response.status_code}: {e.response.text[:200]}")
    except httpx.RequestError as e:
        logger.error(f"WordPress API request error: {str(e)}")
        raise Exception(f"Ошибка соединения с WordPress: {str(e)}")
    except Exception as e:
        logger.error(f"WordPress API unexpected error: {str(e)}")
        raise


# ==================== POSTS ====================

async def wordpress_get_posts(settings: UserSettings, tool_args: Dict[str, Any]) -> str:
    """Получить список постов"""
    per_page = tool_args.get("per_page", 10)
    status = tool_args.get("status", "any")
    
    posts = await wordpress_api_call(
        "GET",
        "/wp-json/wp/v2/posts",
        settings,
        params={"per_page": per_page, "status": status}
    )
    
    result = f"Найдено {len(posts)} постов:\n\n"
    for post in posts:
        result += f"ID: {post['id']}\n"
        result += f"Название: {post['title']['rendered']}\n"
        result += f"Статус: {post['status']}\n"
        result += f"Дата: {post['date']}\n\n"
    
    return result


async def wordpress_create_post(settings: UserSettings, tool_args: Dict[str, Any]) -> str:
    """Создать новый пост"""
    title = tool_args.get("title")
    content = tool_args.get("content")
    status = tool_args.get("status", "draft")
    
    if not title or not content:
        return "❌ Ошибка: title и content обязательны"
    
    post = await wordpress_api_call(
        "POST",
        "/wp-json/wp/v2/posts",
        settings,
        json_data={"title": title, "content": content, "status": status}
    )
    
    return f"✅ Пост создан успешно!\nID: {post['id']}\nНазвание: {post['title']['rendered']}\nСтатус: {post['status']}"


async def wordpress_update_post(settings: UserSettings, tool_args: Dict[str, Any]) -> str:
    """Обновить существующий пост"""
    post_id = tool_args.get("post_id")
    
    if not post_id:
        return "❌ Ошибка: post_id обязателен"
    
    update_data = {}
    if tool_args.get("title"):
        update_data["title"] = tool_args.get("title")
    if tool_args.get("content"):
        update_data["content"] = tool_args.get("content")
    if tool_args.get("status"):
        update_data["status"] = tool_args.get("status")
    
    if not update_data:
        return "❌ Ошибка: укажите хотя бы одно поле для обновления (title, content, status)"
    
    post = await wordpress_api_call(
        "POST",
        f"/wp-json/wp/v2/posts/{post_id}",
        settings,
        json_data=update_data
    )
    
    return f"✅ Пост обновлён!\nID: {post['id']}\nНазвание: {post['title']['rendered']}\nСтатус: {post['status']}"


async def wordpress_delete_post(settings: UserSettings, tool_args: Dict[str, Any]) -> str:
    """Удалить пост"""
    post_id = tool_args.get("post_id")
    
    if not post_id:
        return "❌ Ошибка: post_id обязателен"
    
    await wordpress_api_call(
        "DELETE",
        f"/wp-json/wp/v2/posts/{post_id}",
        settings,
        params={"force": True}
    )
    
    return f"✅ Пост {post_id} успешно удалён"


async def wordpress_search_posts(settings: UserSettings, tool_args: Dict[str, Any]) -> str:
    """Поиск постов по ключевым словам"""
    search_query = tool_args.get("search", "")
    
    if not search_query:
        return "❌ Ошибка: search обязателен"
    
    posts = await wordpress_api_call(
        "GET",
        "/wp-json/wp/v2/posts",
        settings,
        params={"search": search_query, "per_page": 10}
    )
    
    if not posts:
        return f"Ничего не найдено по запросу: {search_query}"
    
    result = f"Найдено {len(posts)} постов по запросу '{search_query}':\n\n"
    for post in posts:
        result += f"ID: {post['id']}\nНазвание: {post['title']['rendered']}\nДата: {post['date']}\n\n"
    
    return result


async def wordpress_bulk_update_posts(settings: UserSettings, tool_args: Dict[str, Any]) -> str:
    """Массовое обновление постов"""
    post_ids = tool_args.get("post_ids", [])
    updates = tool_args.get("updates", {})
    
    if not post_ids:
        return "❌ Ошибка: post_ids обязателен"
    if not updates:
        return "❌ Ошибка: updates обязателен"
    
    updated_count = 0
    errors = []
    
    for post_id in post_ids:
        try:
            await wordpress_api_call(
                "POST",
                f"/wp-json/wp/v2/posts/{post_id}",
                settings,
                json_data=updates
            )
            updated_count += 1
        except Exception as e:
            errors.append(f"Post {post_id}: {str(e)[:100]}")
    
    result = f"✅ Обновлено постов: {updated_count}/{len(post_ids)}"
    if errors:
        result += f"\n\n❌ Ошибки:\n" + "\n".join(errors[:5])
    
    return result


# ==================== PAGES ====================

async def wordpress_get_pages(settings: UserSettings, tool_args: Dict[str, Any]) -> str:
    """Получить список страниц"""
    per_page = tool_args.get("per_page", 10)
    status = tool_args.get("status", "any")
    
    pages = await wordpress_api_call(
        "GET",
        "/wp-json/wp/v2/pages",
        settings,
        params={"per_page": per_page, "status": status}
    )
    
    result = f"Найдено {len(pages)} страниц:\n\n"
    for page in pages:
        result += f"ID: {page['id']}\n"
        result += f"Название: {page['title']['rendered']}\n"
        result += f"Статус: {page['status']}\n"
        result += f"Дата: {page['date']}\n\n"
    
    return result


async def wordpress_create_page(settings: UserSettings, tool_args: Dict[str, Any]) -> str:
    """Создать новую страницу"""
    title = tool_args.get("title")
    content = tool_args.get("content")
    status = tool_args.get("status", "draft")
    parent = tool_args.get("parent", 0)
    
    if not title or not content:
        return "❌ Ошибка: title и content обязательны"
    
    page_data = {
        "title": title,
        "content": content,
        "status": status
    }
    
    if parent:
        page_data["parent"] = parent
    
    page = await wordpress_api_call(
        "POST",
        "/wp-json/wp/v2/pages",
        settings,
        json_data=page_data
    )
    
    return f"✅ Страница создана успешно!\nID: {page['id']}\nНазвание: {page['title']['rendered']}\nСтатус: {page['status']}"


async def wordpress_update_page(settings: UserSettings, tool_args: Dict[str, Any]) -> str:
    """Обновить существующую страницу"""
    page_id = tool_args.get("page_id")
    
    if not page_id:
        return "❌ Ошибка: page_id обязателен"
    
    update_data = {}
    if "title" in tool_args:
        update_data["title"] = tool_args["title"]
    if "content" in tool_args:
        update_data["content"] = tool_args["content"]
    if "status" in tool_args:
        update_data["status"] = tool_args["status"]
    if "parent" in tool_args:
        update_data["parent"] = tool_args["parent"]
    
    if not update_data:
        return "❌ Ошибка: нужно указать хотя бы одно поле для обновления"
    
    page = await wordpress_api_call(
        "POST",
        f"/wp-json/wp/v2/pages/{page_id}",
        settings,
        json_data=update_data
    )
    
    return f"✅ Страница обновлена!\nID: {page['id']}\nНазвание: {page['title']['rendered']}\nСтатус: {page['status']}"


async def wordpress_delete_page(settings: UserSettings, tool_args: Dict[str, Any]) -> str:
    """Удалить страницу"""
    page_id = tool_args.get("page_id")
    
    if not page_id:
        return "❌ Ошибка: page_id обязателен"
    
    await wordpress_api_call(
        "DELETE",
        f"/wp-json/wp/v2/pages/{page_id}",
        settings,
        params={"force": True}
    )
    
    return f"✅ Страница {page_id} успешно удалена"


async def wordpress_search_pages(settings: UserSettings, tool_args: Dict[str, Any]) -> str:
    """Поиск страниц по ключевым словам"""
    search_query = tool_args.get("search", "")
    
    if not search_query:
        return "❌ Ошибка: search обязателен"
    
    pages = await wordpress_api_call(
        "GET",
        "/wp-json/wp/v2/pages",
        settings,
        params={"search": search_query, "per_page": 10}
    )
    
    if not pages:
        return f"Ничего не найдено по запросу: {search_query}"
    
    result = f"Найдено {len(pages)} страниц по запросу '{search_query}':\n\n"
    for page in pages:
        result += f"ID: {page['id']}\nНазвание: {page['title']['rendered']}\nДата: {page['date']}\n\n"
    
    return result


# ==================== CATEGORIES ====================

async def wordpress_create_category(settings: UserSettings, tool_args: Dict[str, Any]) -> str:
    """Создать категорию"""
    name = tool_args.get("name")
    
    if not name:
        return "❌ Ошибка: name обязателен"
    
    category = await wordpress_api_call(
        "POST",
        "/wp-json/wp/v2/categories",
        settings,
        json_data={"name": name}
    )
    
    return f"✅ Категория создана!\nID: {category['id']}\nНазвание: {category['name']}"


async def wordpress_get_categories(settings: UserSettings, tool_args: Dict[str, Any]) -> str:
    """Получить список категорий"""
    categories = await wordpress_api_call(
        "GET",
        "/wp-json/wp/v2/categories",
        settings
    )
    
    result = f"Найдено {len(categories)} категорий:\n\n"
    for cat in categories:
        result += f"ID: {cat['id']}\nНазвание: {cat['name']}\nКоличество постов: {cat['count']}\n\n"
    
    return result


async def wordpress_update_category(settings: UserSettings, tool_args: Dict[str, Any]) -> str:
    """Обновить категорию"""
    category_id = tool_args.get("category_id")
    name = tool_args.get("name")
    
    if not category_id:
        return "❌ Ошибка: category_id обязателен"
    if not name:
        return "❌ Ошибка: name обязателен"
    
    category = await wordpress_api_call(
        "POST",
        f"/wp-json/wp/v2/categories/{category_id}",
        settings,
        json_data={"name": name}
    )
    
    return f"✅ Категория обновлена!\nID: {category['id']}\nНазвание: {category['name']}"


async def wordpress_delete_category(settings: UserSettings, tool_args: Dict[str, Any]) -> str:
    """Удалить категорию"""
    category_id = tool_args.get("category_id")
    
    if not category_id:
        return "❌ Ошибка: category_id обязателен"
    
    await wordpress_api_call(
        "DELETE",
        f"/wp-json/wp/v2/categories/{category_id}",
        settings,
        params={"force": True}
    )
    
    return f"✅ Категория {category_id} успешно удалена"


# ==================== MEDIA ====================

async def wordpress_upload_media(settings: UserSettings, tool_args: Dict[str, Any]) -> str:
    """Загрузить медиафайл"""
    file_url = tool_args.get("file_url")
    title = tool_args.get("title", "Uploaded file")
    
    if not file_url:
        return "❌ Ошибка: file_url обязателен"
    
    try:
        async with httpx.AsyncClient() as client:
            # Скачиваем файл
            file_resp = await client.get(file_url, timeout=60.0)
            file_resp.raise_for_status()
            file_content = file_resp.content
            
            # Загружаем в WordPress
            media = await wordpress_api_call(
                "POST",
                "/wp-json/wp/v2/media",
                settings,
                files={"file": (title, file_content)},
                timeout=60
            )
            
            return f"✅ Медиафайл загружен!\nID: {media['id']}\nURL: {media['source_url']}"
    
    except Exception as e:
        return f"❌ Ошибка загрузки файла: {str(e)}"


async def wordpress_upload_image_from_url(settings: UserSettings, tool_args: Dict[str, Any]) -> str:
    """Загрузить изображение по URL"""
    url = tool_args.get("url")
    
    if not url:
        return "❌ Ошибка: url обязателен"
    
    try:
        async with httpx.AsyncClient() as client:
            # Скачиваем изображение
            img_resp = await client.get(url, timeout=60.0)
            img_resp.raise_for_status()
            img_content = img_resp.content
            
            # Получаем имя файла из URL
            filename = url.split("/")[-1] or "image.jpg"
            
            # Загружаем в WordPress
            media = await wordpress_api_call(
                "POST",
                "/wp-json/wp/v2/media",
                settings,
                files={"file": (filename, img_content)},
                timeout=60
            )
            
            return f"✅ Изображение загружено!\nID: {media['id']}\nURL: {media['source_url']}"
    
    except Exception as e:
        return f"❌ Ошибка загрузки изображения: {str(e)}"


async def wordpress_get_media(settings: UserSettings, tool_args: Dict[str, Any]) -> str:
    """Получить список медиафайлов"""
    per_page = tool_args.get("per_page", 10)
    
    media_items = await wordpress_api_call(
        "GET",
        "/wp-json/wp/v2/media",
        settings,
        params={"per_page": per_page}
    )
    
    result = f"Найдено {len(media_items)} медиафайлов:\n\n"
    for media in media_items:
        result += f"ID: {media['id']}\nНазвание: {media['title']['rendered']}\nURL: {media['source_url']}\n\n"
    
    return result


async def wordpress_delete_media(settings: UserSettings, tool_args: Dict[str, Any]) -> str:
    """Удалить медиафайл"""
    media_id = tool_args.get("media_id")
    
    if not media_id:
        return "❌ Ошибка: media_id обязателен"
    
    await wordpress_api_call(
        "DELETE",
        f"/wp-json/wp/v2/media/{media_id}",
        settings,
        params={"force": True}
    )
    
    return f"✅ Медиафайл {media_id} успешно удалён"


# ==================== COMMENTS ====================

async def wordpress_create_comment(settings: UserSettings, tool_args: Dict[str, Any]) -> str:
    """Создать комментарий"""
    post_id = tool_args.get("post_id")
    content = tool_args.get("content")
    
    if not post_id or not content:
        return "❌ Ошибка: post_id и content обязательны"
    
    comment = await wordpress_api_call(
        "POST",
        "/wp-json/wp/v2/comments",
        settings,
        json_data={"post": post_id, "content": content}
    )
    
    return f"✅ Комментарий создан!\nID: {comment['id']}\nPost ID: {comment['post']}"


async def wordpress_get_comments(settings: UserSettings, tool_args: Dict[str, Any]) -> str:
    """Получить список комментариев"""
    post_id = tool_args.get("post_id")
    
    params = {}
    if post_id:
        params["post"] = post_id
    
    comments = await wordpress_api_call(
        "GET",
        "/wp-json/wp/v2/comments",
        settings,
        params=params
    )
    
    result = f"Найдено {len(comments)} комментариев:\n\n"
    for comment in comments:
        result += f"ID: {comment['id']}\nАвтор: {comment['author_name']}\nСодержание: {comment['content']['rendered'][:100]}...\n\n"
    
    return result


async def wordpress_update_comment(settings: UserSettings, tool_args: Dict[str, Any]) -> str:
    """Обновить комментарий"""
    comment_id = tool_args.get("comment_id")
    content = tool_args.get("content")
    
    if not comment_id:
        return "❌ Ошибка: comment_id обязателен"
    if not content:
        return "❌ Ошибка: content обязателен"
    
    comment = await wordpress_api_call(
        "POST",
        f"/wp-json/wp/v2/comments/{comment_id}",
        settings,
        json_data={"content": content}
    )
    
    return f"✅ Комментарий {comment['id']} обновлён"


async def wordpress_delete_comment(settings: UserSettings, tool_args: Dict[str, Any]) -> str:
    """Удалить комментарий"""
    comment_id = tool_args.get("comment_id")
    
    if not comment_id:
        return "❌ Ошибка: comment_id обязателен"
    
    await wordpress_api_call(
        "DELETE",
        f"/wp-json/wp/v2/comments/{comment_id}",
        settings,
        params={"force": True}
    )
    
    return f"✅ Комментарий {comment_id} успешно удалён"


# ==================== TOOL ROUTER ====================

async def handle_wordpress_tool(tool_name: str, settings: UserSettings, tool_args: Dict[str, Any]) -> str:
    """
    Роутер для всех WordPress инструментов
    
    Args:
        tool_name: Название инструмента
        settings: Настройки пользователя
        tool_args: Аргументы инструмента
    
    Returns:
        Результат выполнения в виде строки
    """
    # Валидация настроек
    is_valid, error_msg = await validate_wordpress_settings(settings)
    if not is_valid:
        return f"❌ {error_msg}"
    
    # Маппинг инструментов
    tools_map = {
        "wordpress_get_posts": wordpress_get_posts,
        "wordpress_create_post": wordpress_create_post,
        "wordpress_update_post": wordpress_update_post,
        "wordpress_delete_post": wordpress_delete_post,
        "wordpress_search_posts": wordpress_search_posts,
        "wordpress_bulk_update_posts": wordpress_bulk_update_posts,
        "wordpress_create_category": wordpress_create_category,
        "wordpress_get_categories": wordpress_get_categories,
        "wordpress_update_category": wordpress_update_category,
        "wordpress_delete_category": wordpress_delete_category,
        "wordpress_upload_media": wordpress_upload_media,
        "wordpress_upload_image_from_url": wordpress_upload_image_from_url,
        "wordpress_get_media": wordpress_get_media,
        "wordpress_delete_media": wordpress_delete_media,
        "wordpress_create_comment": wordpress_create_comment,
        "wordpress_get_comments": wordpress_get_comments,
        "wordpress_update_comment": wordpress_update_comment,
        "wordpress_delete_comment": wordpress_delete_comment,
    }
    
    handler = tools_map.get(tool_name)
    if not handler:
        return f"❌ Неизвестный WordPress инструмент: {tool_name}"
    
    try:
        return await handler(settings, tool_args)
    except Exception as e:
        logger.error(f"WordPress tool {tool_name} error: {str(e)}")
        return f"❌ Ошибка выполнения {tool_name}: {str(e)}"

