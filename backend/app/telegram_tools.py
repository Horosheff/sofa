"""
Telegram Bot Tools для MCP Platform
Интеграция с Telegram Bot API для базовых операций
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter
from sqlalchemy.orm import Session
from telegram import (
    Bot,
    BotCommand,
    InputMediaDocument,
    InputMediaPhoto,
    InputMediaVideo,
)
from telegram.error import TelegramError

from app.database import get_db
from app.models import UserSettings
from app.helpers import decrypt_token

logger = logging.getLogger(__name__)

router = APIRouter()

async def get_bot_from_settings(user_id: str, db: Session) -> Optional[Bot]:
    """Получить экземпляр бота из настроек пользователя."""
    try:
        settings = (
            db.query(UserSettings)
            .filter(UserSettings.user_id == user_id)
            .first()
        )
        if not settings or not settings.telegram_bot_token:
            return None

        bot_token = decrypt_token(settings.telegram_bot_token)
        return Bot(token=bot_token)
    except Exception as exc:
        logger.error("Ошибка инициализации Telegram бота для пользователя %s: %s", user_id, exc)
        return None

async def send_message(params: Dict[str, Any], user_id: str, db: Session) -> str:
    bot = await get_bot_from_settings(user_id, db)
    if not bot:
        return "❌ Telegram бот не настроен. Укажите токен в настройках."

    chat_id = params.get("chat_id")
    text = params.get("text")
    parse_mode = params.get("parse_mode")
    disable_web_page_preview = params.get("disable_web_page_preview", False)
    disable_notification = params.get("disable_notification", False)
    reply_to_message_id = params.get("reply_to_message_id")

    if not chat_id or not text:
        return "❌ Необходимо указать параметры chat_id и text."

    try:
        message = await bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode=parse_mode,
            disable_web_page_preview=disable_web_page_preview,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
        )
        return (
            f"✅ Сообщение отправлено!\n"
            f"Chat ID: {message.chat.id}\n"
            f"Message ID: {message.message_id}"
        )
    except TelegramError as exc:
        return f"❌ Ошибка Telegram API: {exc.message}"
    except Exception as exc:
        logger.error("Ошибка отправки сообщения: %s", exc, exc_info=True)
        return f"❌ Внутренняя ошибка: {exc}"

async def send_photo(params: Dict[str, Any], user_id: str, db: Session) -> str:
    bot = await get_bot_from_settings(user_id, db)
    if not bot:
        return "❌ Telegram бот не настроен."

    chat_id = params.get("chat_id")
    photo = params.get("photo")
    caption = params.get("caption")
    parse_mode = params.get("parse_mode")

    if not chat_id or not photo:
        return "❌ Необходимо указать chat_id и photo."

    try:
        message = await bot.send_photo(
            chat_id=chat_id,
            photo=photo,
            caption=caption,
            parse_mode=parse_mode,
        )
        sizes = ", ".join(f"{size.width}x{size.height}" for size in message.photo)
        return (
            f"✅ Фото отправлено!\n"
            f"Message ID: {message.message_id}\n"
            f"Размеры: {sizes or 'не определены'}"
        )
    except TelegramError as exc:
        return f"❌ Ошибка Telegram API: {exc.message}"
    except Exception as exc:
        logger.error("Ошибка отправки фото: %s", exc, exc_info=True)
        return f"❌ Внутренняя ошибка: {exc}"

async def send_document(params: Dict[str, Any], user_id: str, db: Session) -> str:
    bot = await get_bot_from_settings(user_id, db)
    if not bot:
        return "❌ Telegram бот не настроен."

    chat_id = params.get("chat_id")
    document = params.get("document")
    caption = params.get("caption")
    parse_mode = params.get("parse_mode")

    if not chat_id or not document:
        return "❌ Необходимо указать chat_id и document."

    try:
        message = await bot.send_document(
            chat_id=chat_id,
            document=document,
            caption=caption,
            parse_mode=parse_mode,
        )
        file_name = message.document.file_name if message.document else ""
        return (
            f"✅ Документ отправлен!\n"
            f"Message ID: {message.message_id}\n"
            f"Файл: {file_name or 'без имени'}"
        )
    except TelegramError as exc:
        return f"❌ Ошибка Telegram API: {exc.message}"
    except Exception as exc:
        logger.error("Ошибка отправки документа: %s", exc, exc_info=True)
        return f"❌ Внутренняя ошибка: {exc}"

async def send_media_group(params: Dict[str, Any], user_id: str, db: Session) -> str:
    bot = await get_bot_from_settings(user_id, db)
    if not bot:
        return "❌ Telegram бот не настроен."

    chat_id = params.get("chat_id")
    media_items = params.get("media")

    if not chat_id or not media_items:
        return "❌ Необходимо указать chat_id и массив media."

    media: List[InputMediaDocument | InputMediaPhoto | InputMediaVideo] = []
    for item in media_items:
        item_type = item.get("type")
        media_value = item.get("media")
        caption = item.get("caption")
        parse_mode = item.get("parse_mode")

        if not item_type or not media_value:
            return "❌ Каждый элемент media должен содержать type и media."

        if item_type == "photo":
            media.append(InputMediaPhoto(media=media_value, caption=caption, parse_mode=parse_mode))
        elif item_type == "video":
            media.append(InputMediaVideo(media=media_value, caption=caption, parse_mode=parse_mode))
        elif item_type == "document":
            media.append(InputMediaDocument(media=media_value, caption=caption, parse_mode=parse_mode))
        else:
            return f"❌ Тип media '{item_type}' не поддерживается (доступно: photo, video, document)."

    try:
        messages = await bot.send_media_group(chat_id=chat_id, media=media)
        message_ids = ", ".join(str(msg.message_id) for msg in messages)
        return (
            f"✅ Медиа-группа отправлена!\n"
            f"Всего сообщений: {len(messages)}\n"
            f"Message IDs: {message_ids}"
        )
    except TelegramError as exc:
        return f"❌ Ошибка Telegram API: {exc.message}"
    except Exception as exc:
        logger.error("Ошибка отправки media group: %s", exc, exc_info=True)
        return f"❌ Внутренняя ошибка: {exc}"

async def send_audio(params: Dict[str, Any], user_id: str, db: Session) -> str:
    bot = await get_bot_from_settings(user_id, db)
    if not bot:
        return "❌ Telegram бот не настроен."

    chat_id = params.get("chat_id")
    audio = params.get("audio")
    caption = params.get("caption")
    parse_mode = params.get("parse_mode")

    if not chat_id or not audio:
        return "❌ Необходимо указать chat_id и audio."

    try:
        message = await bot.send_audio(
            chat_id=chat_id,
            audio=audio,
            caption=caption,
            parse_mode=parse_mode,
        )
        duration = message.audio.duration if message.audio else "?"
        return (
            f"✅ Аудио отправлено!\n"
            f"Message ID: {message.message_id}\n"
            f"Длительность: {duration} сек."
        )
    except TelegramError as exc:
        return f"❌ Ошибка Telegram API: {exc.message}"
    except Exception as exc:
        logger.error("Ошибка отправки аудио: %s", exc, exc_info=True)
        return f"❌ Внутренняя ошибка: {exc}"

async def send_video(params: Dict[str, Any], user_id: str, db: Session) -> str:
    bot = await get_bot_from_settings(user_id, db)
    if not bot:
        return "❌ Telegram бот не настроен."

    chat_id = params.get("chat_id")
    video = params.get("video")
    caption = params.get("caption")
    parse_mode = params.get("parse_mode")

    if not chat_id or not video:
        return "❌ Необходимо указать chat_id и video."

    try:
        message = await bot.send_video(
            chat_id=chat_id,
            video=video,
            caption=caption,
            parse_mode=parse_mode,
        )
        duration = message.video.duration if message.video else "?"
        return (
            f"✅ Видео отправлено!\n"
            f"Message ID: {message.message_id}\n"
            f"Длительность: {duration} сек."
        )
    except TelegramError as exc:
        return f"❌ Ошибка Telegram API: {exc.message}"
    except Exception as exc:
        logger.error("Ошибка отправки видео: %s", exc, exc_info=True)
        return f"❌ Внутренняя ошибка: {exc}"

async def send_animation(params: Dict[str, Any], user_id: str, db: Session) -> str:
    bot = await get_bot_from_settings(user_id, db)
    if not bot:
        return "❌ Telegram бот не настроен."

    chat_id = params.get("chat_id")
    animation = params.get("animation")
    caption = params.get("caption")
    parse_mode = params.get("parse_mode")

    if not chat_id or not animation:
        return "❌ Необходимо указать chat_id и animation."

    try:
        message = await bot.send_animation(
            chat_id=chat_id,
            animation=animation,
            caption=caption,
            parse_mode=parse_mode,
        )
        return (
            f"✅ Анимация отправлена!\n"
            f"Message ID: {message.message_id}"
        )
    except TelegramError as exc:
        return f"❌ Ошибка Telegram API: {exc.message}"
    except Exception as exc:
        logger.error("Ошибка отправки анимации: %s", exc, exc_info=True)
        return f"❌ Внутренняя ошибка: {exc}"

async def set_webhook(params: Dict[str, Any], user_id: str, db: Session) -> str:
    bot = await get_bot_from_settings(user_id, db)
    if not bot:
        return "❌ Telegram бот не настроен."

    url = params.get("url")
    if not url:
        return "❌ Необходимо указать параметр url."

    try:
        result = await bot.set_webhook(
            url=url,
            secret_token=params.get("secret_token"),
            allowed_updates=params.get("allowed_updates"),
        )
        return "✅ Webhook успешно установлен." if result else "⚠️ Не удалось установить webhook."
    except TelegramError as exc:
        return f"❌ Ошибка Telegram API: {exc.message}"
    except Exception as exc:
        logger.error("Ошибка установки webhook: %s", exc, exc_info=True)
        return f"❌ Внутренняя ошибка: {exc}"

async def delete_webhook(params: Dict[str, Any], user_id: str, db: Session) -> str:
    bot = await get_bot_from_settings(user_id, db)
    if not bot:
        return "❌ Telegram бот не настроен."

    drop_pending = params.get("drop_pending_updates", False)

    try:
        result = await bot.delete_webhook(drop_pending_updates=drop_pending)
        status = "✅ Webhook удалён." if result else "⚠️ Не удалось удалить webhook."
        if drop_pending:
            status += " (Подписанные обновления отменены)"
        return status
    except TelegramError as exc:
        return f"❌ Ошибка Telegram API: {exc.message}"
    except Exception as exc:
        logger.error("Ошибка удаления webhook: %s", exc, exc_info=True)
        return f"❌ Внутренняя ошибка: {exc}"

async def get_webhook_info(params: Dict[str, Any], user_id: str, db: Session) -> str:
    bot = await get_bot_from_settings(user_id, db)
    if not bot:
        return "❌ Telegram бот не настроен."

    try:
        info = await bot.get_webhook_info()
        return (
            "🌐 Webhook информация:\n"
            f"URL: {info.url or 'не установлен'}\n"
            f"Pending updates: {info.pending_update_count}\n"
            f"Последняя ошибка: {info.last_error_message or 'нет'}"
        )
    except TelegramError as exc:
        return f"❌ Ошибка Telegram API: {exc.message}"
    except Exception as exc:
        logger.error("Ошибка получения webhook info: %s", exc, exc_info=True)
        return f"❌ Внутренняя ошибка: {exc}"

async def get_bot_info(params: Dict[str, Any], user_id: str, db: Session) -> str:
    bot = await get_bot_from_settings(user_id, db)
    if not bot:
        return "❌ Telegram бот не настроен."

    try:
        info = await bot.get_me()
        return (
            "🤖 Информация о боте:\n"
            f"ID: {info.id}\n"
            f"Username: @{info.username}\n"
            f"Имя: {info.first_name}\n"
            f"Поддерживает inline: {'да' if info.supports_inline_queries else 'нет'}"
        )
    except TelegramError as exc:
        return f"❌ Ошибка Telegram API: {exc.message}"
    except Exception as exc:
        logger.error("Ошибка получения информации о боте: %s", exc, exc_info=True)
        return f"❌ Внутренняя ошибка: {exc}"

async def get_updates(params: Dict[str, Any], user_id: str, db: Session) -> str:
    bot = await get_bot_from_settings(user_id, db)
    if not bot:
        return "❌ Telegram бот не настроен."

    try:
        updates = await bot.get_updates(
            offset=params.get("offset"),
            limit=params.get("limit"),
            timeout=params.get("timeout", 0),
        )
        if not updates:
            return "ℹ️ Обновлений нет."

        summary_lines = [f"Всего обновлений: {len(updates)}"]
        for update in updates[:10]:
            if update.message:
                author = update.message.from_user
                author_text = f"@{author.username}" if author and author.username else "пользователь"
                summary_lines.append(
                    f"• Message {update.update_id}: {author_text} → {update.message.chat.id}"
                )
            elif update.callback_query:
                summary_lines.append(
                    f"• Callback {update.update_id}: {update.callback_query.data}"
                )
            else:
                summary_lines.append(f"• Update {update.update_id}: тип {update.to_dict().keys()}")

        if len(updates) > 10:
            summary_lines.append("… показаны первые 10 обновлений …")

        return "\n".join(summary_lines)
    except TelegramError as exc:
        return f"❌ Ошибка Telegram API: {exc.message}"
    except Exception as exc:
        logger.error("Ошибка получения обновлений: %s", exc, exc_info=True)
        return f"❌ Внутренняя ошибка: {exc}"

async def set_commands(params: Dict[str, Any], user_id: str, db: Session) -> str:
    bot = await get_bot_from_settings(user_id, db)
    if not bot:
        return "❌ Telegram бот не настроен."

    commands_data = params.get("commands", [])
    if not commands_data:
        return "❌ Передайте список commands (command + description)."

    try:
        commands = [
            BotCommand(command=cmd["command"], description=cmd["description"])
            for cmd in commands_data
            if cmd.get("command") and cmd.get("description")
        ]
        if not commands:
            return "❌ Список команд пуст или некорректен."

        await bot.set_my_commands(commands)
        titles = ", ".join(f"/{cmd.command}" for cmd in commands)
        return f"✅ Команды установлены: {titles}"
    except TelegramError as exc:
        return f"❌ Ошибка Telegram API: {exc.message}"
    except Exception as exc:
        logger.error("Ошибка установки команд: %s", exc, exc_info=True)
        return f"❌ Внутренняя ошибка: {exc}"

async def delete_message(params: Dict[str, Any], user_id: str, db: Session) -> str:
    bot = await get_bot_from_settings(user_id, db)
    if not bot:
        return "❌ Telegram бот не настроен."

    chat_id = params.get("chat_id")
    message_id = params.get("message_id")

    if not chat_id or not message_id:
        return "❌ Необходимо указать chat_id и message_id."

    try:
        result = await bot.delete_message(chat_id=chat_id, message_id=message_id)
        return "✅ Сообщение удалено." if result else "⚠️ Не удалось удалить сообщение."
    except TelegramError as exc:
        return f"❌ Ошибка Telegram API: {exc.message}"
    except Exception as exc:
        logger.error("Ошибка удаления сообщения: %s", exc, exc_info=True)
        return f"❌ Внутренняя ошибка: {exc}"

async def edit_message(params: Dict[str, Any], user_id: str, db: Session) -> str:
    bot = await get_bot_from_settings(user_id, db)
    if not bot:
        return "❌ Telegram бот не настроен."

    chat_id = params.get("chat_id")
    message_id = params.get("message_id")
    new_text = params.get("text")
    parse_mode = params.get("parse_mode")

    if not chat_id or not message_id or not new_text:
        return "❌ Необходимо указать chat_id, message_id и text."

    try:
        message = await bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=new_text,
            parse_mode=parse_mode,
        )
        return f"✅ Сообщение {message.message_id} обновлено."
    except TelegramError as exc:
        return f"❌ Ошибка Telegram API: {exc.message}"
    except Exception as exc:
        logger.error("Ошибка редактирования сообщения: %s", exc, exc_info=True)
        return f"❌ Внутренняя ошибка: {exc}"

async def send_poll(params: Dict[str, Any], user_id: str, db: Session) -> str:
    bot = await get_bot_from_settings(user_id, db)
    if not bot:
        return "❌ Telegram бот не настроен."

    chat_id = params.get("chat_id")
    question = params.get("question")
    options = params.get("options")

    if not chat_id or not question or not options:
        return "❌ Необходимо указать chat_id, question и options (список)."

    try:
        message = await bot.send_poll(
            chat_id=chat_id,
            question=question,
            options=options,
            allows_multiple_answers=params.get("allows_multiple_answers", False),
            is_anonymous=params.get("is_anonymous", True),
        )
        return f"✅ Опрос отправлен. Message ID: {message.message_id}"
    except TelegramError as exc:
        return f"❌ Ошибка Telegram API: {exc.message}"
    except Exception as exc:
        logger.error("Ошибка отправки опроса: %s", exc, exc_info=True)
        return f"❌ Внутренняя ошибка: {exc}"

async def stop_poll(params: Dict[str, Any], user_id: str, db: Session) -> str:
    bot = await get_bot_from_settings(user_id, db)
    if not bot:
        return "❌ Telegram бот не настроен."

    chat_id = params.get("chat_id")
    message_id = params.get("message_id")

    if not chat_id or not message_id:
        return "❌ Необходимо указать chat_id и message_id."

    try:
        poll = await bot.stop_poll(chat_id=chat_id, message_id=message_id)
        total_votes = sum(option.voter_count for option in poll.options)
        return f"✅ Опрос остановлен. Всего голосов: {total_votes}"
    except TelegramError as exc:
        return f"❌ Ошибка Telegram API: {exc.message}"
    except Exception as exc:
        logger.error("Ошибка остановки опроса: %s", exc, exc_info=True)
        return f"❌ Внутренняя ошибка: {exc}"

async def answer_callback_query(params: Dict[str, Any], user_id: str, db: Session) -> str:
    bot = await get_bot_from_settings(user_id, db)
    if not bot:
        return "❌ Telegram бот не настроен."

    callback_query_id = params.get("callback_query_id")
    if not callback_query_id:
        return "❌ Необходимо указать callback_query_id."

    text = params.get("text")
    show_alert = params.get("show_alert", False)
    url = params.get("url")

    try:
        await bot.answer_callback_query(
            callback_query_id=callback_query_id,
            text=text,
            show_alert=show_alert,
            url=url,
        )
        return "✅ Callback query обработан."
    except TelegramError as exc:
        return f"❌ Ошибка Telegram API: {exc.message}"
    except Exception as exc:
        logger.error("Ошибка answer_callback_query: %s", exc, exc_info=True)
        return f"❌ Внутренняя ошибка: {exc}"

async def send_chat_action(params: Dict[str, Any], user_id: str, db: Session) -> str:
    bot = await get_bot_from_settings(user_id, db)
    if not bot:
        return "❌ Telegram бот не настроен."

    chat_id = params.get("chat_id")
    action = params.get("action", "typing")

    if not chat_id:
        return "❌ Необходимо указать chat_id."

    try:
        await bot.send_chat_action(chat_id=chat_id, action=action)
        return f"✅ Действие '{action}' отправлено в чат {chat_id}."
    except TelegramError as exc:
        return f"❌ Ошибка Telegram API: {exc.message}"
    except Exception as exc:
        logger.error("Ошибка отправки chat_action: %s", exc, exc_info=True)
        return f"❌ Внутренняя ошибка: {exc}"

async def get_user_profile_photos(params: Dict[str, Any], user_id: str, db: Session) -> str:
    bot = await get_bot_from_settings(user_id, db)
    if not bot:
        return "❌ Telegram бот не настроен."

    target_user_id = params.get("user_id")
    if not target_user_id:
        return "❌ Необходимо указать user_id."

    limit = params.get("limit", 5)

    try:
        photos = await bot.get_user_profile_photos(user_id=target_user_id, limit=limit)
        if photos.total_count == 0:
            return f"ℹ️ У пользователя {target_user_id} нет аватаров."

        lines = [f"Всего фото: {photos.total_count}"]
        for idx, photo_sizes in enumerate(photos.photos[:limit], start=1):
            largest = photo_sizes[-1]
            lines.append(
                f"• Фото {idx}: file_id={largest.file_id}, размер={largest.width}x{largest.height}"
            )
        return "\n".join(lines)
    except TelegramError as exc:
        return f"❌ Ошибка Telegram API: {exc.message}"
    except Exception as exc:
        logger.error("Ошибка получения user_profile_photos: %s", exc, exc_info=True)
        return f"❌ Внутренняя ошибка: {exc}"

async def get_file(params: Dict[str, Any], user_id: str, db: Session) -> str:
    bot = await get_bot_from_settings(user_id, db)
    if not bot:
        return "❌ Telegram бот не настроен."

    file_id = params.get("file_id")
    if not file_id:
        return "❌ Необходимо указать file_id."

    try:
        file = await bot.get_file(file_id)
        return (
            "✅ Файл найден:\n"
            f"File ID: {file.file_id}\n"
            f"File Path: {file.file_path}\n"
            f"File Size: {file.file_size} байт"
        )
    except TelegramError as exc:
        return f"❌ Ошибка Telegram API: {exc.message}"
    except Exception as exc:
        logger.error("Ошибка получения файла: %s", exc, exc_info=True)
        return f"❌ Внутренняя ошибка: {exc}"

TOOLS_MAP = {
    "telegram_send_message": send_message,
    "telegram_send_photo": send_photo,
    "telegram_send_document": send_document,
    "telegram_send_media_group": send_media_group,
    "telegram_send_audio": send_audio,
    "telegram_send_video": send_video,
    "telegram_send_animation": send_animation,
    "telegram_set_webhook": set_webhook,
    "telegram_delete_webhook": delete_webhook,
    "telegram_get_webhook_info": get_webhook_info,
    "telegram_get_bot_info": get_bot_info,
    "telegram_get_updates": get_updates,
    "telegram_set_commands": set_commands,
    "telegram_delete_message": delete_message,
    "telegram_edit_message": edit_message,
    "telegram_send_poll": send_poll,
    "telegram_stop_poll": stop_poll,
    "telegram_answer_callback_query": answer_callback_query,
    "telegram_send_chat_action": send_chat_action,
    "telegram_get_user_profile_photos": get_user_profile_photos,
    "telegram_get_file": get_file,
}


async def handle_telegram_tool(tool_name: str, params: Dict[str, Any], user_id: str, db: Session) -> str:
    """Маршрутизация Telegram инструментов."""
    handler = TOOLS_MAP.get(tool_name)
    if not handler:
        return f"❌ Инструмент '{tool_name}' отключён или не реализован."

    try:
        return await handler(params or {}, user_id, db)
    except Exception as exc:
        logger.error("Критическая ошибка Telegram инструмента %s: %s", tool_name, exc, exc_info=True)
        return f"❌ Внутренняя ошибка выполнения инструмента: {exc}"