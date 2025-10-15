"""
Telegram Bot Tools для MCP Platform
Интеграция с Telegram Bot API для управления ботами
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from telegram.error import TelegramError

from .database import get_db
from .models import User, UserSettings
from .helpers import create_jsonrpc_response, create_jsonrpc_error, JSONRPCErrorCodes

logger = logging.getLogger(__name__)

# Глобальное хранилище для ботов
bot_applications: Dict[str, Application] = {}

router = APIRouter()

# Словарь для маршрутизации инструментов Telegram
tools_map = {
    "telegram_create_bot": "create_bot",
    "telegram_send_message": "send_message", 
    "telegram_send_photo": "send_photo",
    "telegram_send_document": "send_document",
    "telegram_set_webhook": "set_webhook",
    "telegram_delete_webhook": "delete_webhook",
    "telegram_get_webhook_info": "get_webhook_info",
    "telegram_get_bot_info": "get_bot_info",
    "telegram_get_updates": "get_updates",
    "telegram_set_commands": "set_commands",
    "telegram_get_commands": "get_commands",
    "telegram_delete_message": "delete_message",
    "telegram_edit_message": "edit_message",
    "telegram_pin_message": "pin_message",
    "telegram_unpin_message": "unpin_message",
    "telegram_get_chat": "get_chat",
    "telegram_get_chat_member": "get_chat_member",
    "telegram_ban_chat_member": "ban_chat_member",
    "telegram_unban_chat_member": "unban_chat_member",
    "telegram_promote_chat_member": "promote_chat_member",
    "telegram_restrict_chat_member": "restrict_chat_member",
    "telegram_export_chat_invite_link": "export_chat_invite_link",
    "telegram_create_chat_invite_link": "create_chat_invite_link",
    "telegram_revoke_chat_invite_link": "revoke_chat_invite_link",
    "telegram_approve_chat_join_request": "approve_chat_join_request",
    "telegram_decline_chat_join_request": "decline_chat_join_request",
    "telegram_set_chat_photo": "set_chat_photo",
    "telegram_delete_chat_photo": "delete_chat_photo",
    "telegram_set_chat_title": "set_chat_title",
    "telegram_set_chat_description": "set_chat_description",
    "telegram_pin_chat_message": "pin_chat_message",
    "telegram_unpin_chat_message": "unpin_chat_message",
    "telegram_unpin_all_chat_messages": "unpin_all_chat_messages",
    "telegram_leave_chat": "leave_chat",
    "telegram_answer_callback_query": "answer_callback_query",
    "telegram_answer_inline_query": "answer_inline_query",
    "telegram_stop_poll": "stop_poll",
    "telegram_send_poll": "send_poll",
    "telegram_send_dice": "send_dice",
    "telegram_send_game": "send_game",
    "telegram_send_invoice": "send_invoice",
    "telegram_send_media_group": "send_media_group",
    "telegram_send_animation": "send_animation",
    "telegram_send_audio": "send_audio",
    "telegram_send_video": "send_video",
    "telegram_send_video_note": "send_video_note",
    "telegram_send_voice": "send_voice",
    "telegram_send_sticker": "send_sticker",
    "telegram_get_sticker_set": "get_sticker_set",
    "telegram_upload_sticker_file": "upload_sticker_file",
    "telegram_create_new_sticker_set": "create_new_sticker_set",
    "telegram_add_sticker_to_set": "add_sticker_to_set",
    "telegram_set_sticker_position_in_set": "set_sticker_position_in_set",
    "telegram_delete_sticker_from_set": "delete_sticker_from_set",
    "telegram_set_sticker_set_thumb": "set_sticker_set_thumb",
    "telegram_send_chat_action": "send_chat_action",
    "telegram_get_user_profile_photos": "get_user_profile_photos",
    "telegram_get_file": "get_file",
    "telegram_kick_chat_member": "kick_chat_member",
    "telegram_set_chat_administrator_custom_title": "set_chat_administrator_custom_title",
    "telegram_ban_chat_sender_chat": "ban_chat_sender_chat",
    "telegram_unban_chat_sender_chat": "unban_chat_sender_chat",
    "telegram_set_chat_permissions": "set_chat_permissions",
    "telegram_edit_chat_invite_link": "edit_chat_invite_link",
    "telegram_set_chat_sticker_set": "set_chat_sticker_set",
    "telegram_delete_chat_sticker_set": "delete_chat_sticker_set"
}

async def get_bot_from_settings(user_id: str, db: Session) -> Optional[Bot]:
    """Получить бота из настроек пользователя"""
    try:
        user_settings = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
        if not user_settings or not user_settings.telegram_bot_token:
            return None
        
        bot = Bot(token=user_settings.telegram_bot_token)
        return bot
    except Exception as e:
        logger.error(f"Ошибка получения бота для пользователя {user_id}: {e}")
        return None

# Основные методы Telegram Bot API

async def create_bot(params: Dict[str, Any], user_id: str, db: Session) -> Dict[str, Any]:
    """Создать нового бота"""
    try:
        bot_token = params.get("bot_token")
        if not bot_token:
            return create_jsonrpc_error(
                JSONRPCErrorCodes.INVALID_PARAMS,
                "bot_token is required"
            )
        
        # Проверяем токен бота
        bot = Bot(token=bot_token)
        bot_info = await bot.get_me()
        
        # Сохраняем токен в настройки пользователя
        user_settings = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
        if not user_settings:
            user_settings = UserSettings(user_id=user_id)
            db.add(user_settings)
        
        user_settings.telegram_bot_token = bot_token
        db.commit()
        
        return create_jsonrpc_response({
            "bot_id": bot_info.id,
            "username": bot_info.username,
            "first_name": bot_info.first_name,
            "can_join_groups": bot_info.can_join_groups,
            "can_read_all_group_messages": bot_info.can_read_all_group_messages,
            "supports_inline_queries": bot_info.supports_inline_queries
        })
        
    except TelegramError as e:
        return create_jsonrpc_error(
            JSONRPCErrorCodes.INVALID_PARAMS,
            f"Invalid bot token: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Ошибка создания бота: {e}")
        return create_jsonrpc_error(
            JSONRPCErrorCodes.INTERNAL_ERROR,
            f"Internal error: {str(e)}"
        )

async def send_message(params: Dict[str, Any], user_id: str, db: Session) -> Dict[str, Any]:
    """Отправить сообщение"""
    try:
        bot = await get_bot_from_settings(user_id, db)
        if not bot:
            return create_jsonrpc_error(
                JSONRPCErrorCodes.INVALID_PARAMS,
                "Bot not configured"
            )
        
        chat_id = params.get("chat_id")
        text = params.get("text")
        parse_mode = params.get("parse_mode", "HTML")
        reply_to_message_id = params.get("reply_to_message_id")
        disable_web_page_preview = params.get("disable_web_page_preview", False)
        disable_notification = params.get("disable_notification", False)
        
        if not chat_id or not text:
            return create_jsonrpc_error(
                JSONRPCErrorCodes.INVALID_PARAMS,
                "chat_id and text are required"
            )
        
        message = await bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode=parse_mode,
            reply_to_message_id=reply_to_message_id,
            disable_web_page_preview=disable_web_page_preview,
            disable_notification=disable_notification
        )
        
        return create_jsonrpc_response({
            "message_id": message.message_id,
            "date": message.date.isoformat(),
            "chat": {
                "id": message.chat.id,
                "type": message.chat.type,
                "title": message.chat.title,
                "username": message.chat.username
            },
            "text": message.text
        })
        
    except TelegramError as e:
        return create_jsonrpc_error(
            JSONRPCErrorCodes.INTERNAL_ERROR,
            f"Telegram error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Ошибка отправки сообщения: {e}")
        return create_jsonrpc_error(
            JSONRPCErrorCodes.INTERNAL_ERROR,
            f"Internal error: {str(e)}"
        )

async def send_photo(params: Dict[str, Any], user_id: str, db: Session) -> Dict[str, Any]:
    """Отправить фото"""
    try:
        bot = await get_bot_from_settings(user_id, db)
        if not bot:
            return create_jsonrpc_error(
                JSONRPCErrorCodes.INVALID_PARAMS,
                "Bot not configured"
            )
        
        chat_id = params.get("chat_id")
        photo = params.get("photo")  # URL или file_id
        caption = params.get("caption", "")
        parse_mode = params.get("parse_mode", "HTML")
        
        if not chat_id or not photo:
            return create_jsonrpc_error(
                JSONRPCErrorCodes.INVALID_PARAMS,
                "chat_id and photo are required"
            )
        
        message = await bot.send_photo(
            chat_id=chat_id,
            photo=photo,
            caption=caption,
            parse_mode=parse_mode
        )
        
        return create_jsonrpc_response({
            "message_id": message.message_id,
            "date": message.date.isoformat(),
            "chat": {
                "id": message.chat.id,
                "type": message.chat.type
            },
            "photo": [{"file_id": p.file_id, "file_unique_id": p.file_unique_id} for p in message.photo]
        })
        
    except Exception as e:
        logger.error(f"Ошибка отправки фото: {e}")
        return create_jsonrpc_error(
            JSONRPCErrorCodes.INTERNAL_ERROR,
            f"Internal error: {str(e)}"
        )

async def set_webhook(params: Dict[str, Any], user_id: str, db: Session) -> Dict[str, Any]:
    """Установить webhook"""
    try:
        bot = await get_bot_from_settings(user_id, db)
        if not bot:
            return create_jsonrpc_error(
                JSONRPCErrorCodes.INVALID_PARAMS,
                "Bot not configured"
            )
        
        url = params.get("url")
        if not url:
            return create_jsonrpc_error(
                JSONRPCErrorCodes.INVALID_PARAMS,
                "url is required"
            )
        
        result = await bot.set_webhook(url=url)
        
        return create_jsonrpc_response({
            "ok": result,
            "description": "Webhook was set successfully" if result else "Failed to set webhook"
        })
        
    except Exception as e:
        logger.error(f"Ошибка установки webhook: {e}")
        return create_jsonrpc_error(
            JSONRPCErrorCodes.INTERNAL_ERROR,
            f"Internal error: {str(e)}"
        )

async def get_bot_info(params: Dict[str, Any], user_id: str, db: Session) -> Dict[str, Any]:
    """Получить информацию о боте"""
    try:
        bot = await get_bot_from_settings(user_id, db)
        if not bot:
            return create_jsonrpc_error(
                JSONRPCErrorCodes.INVALID_PARAMS,
                "Bot not configured"
            )
        
        bot_info = await bot.get_me()
        
        return create_jsonrpc_response({
            "id": bot_info.id,
            "is_bot": bot_info.is_bot,
            "first_name": bot_info.first_name,
            "last_name": bot_info.last_name,
            "username": bot_info.username,
            "language_code": bot_info.language_code,
            "can_join_groups": bot_info.can_join_groups,
            "can_read_all_group_messages": bot_info.can_read_all_group_messages,
            "supports_inline_queries": bot_info.supports_inline_queries
        })
        
    except Exception as e:
        logger.error(f"Ошибка получения информации о боте: {e}")
        return create_jsonrpc_error(
            JSONRPCErrorCodes.INTERNAL_ERROR,
            f"Internal error: {str(e)}"
        )

async def get_updates(params: Dict[str, Any], user_id: str, db: Session) -> Dict[str, Any]:
    """Получить обновления"""
    try:
        bot = await get_bot_from_settings(user_id, db)
        if not bot:
            return create_jsonrpc_error(
                JSONRPCErrorCodes.INVALID_PARAMS,
                "Bot not configured"
            )
        
        offset = params.get("offset", 0)
        limit = params.get("limit", 100)
        timeout = params.get("timeout", 0)
        
        updates = await bot.get_updates(
            offset=offset,
            limit=limit,
            timeout=timeout
        )
        
        updates_data = []
        for update in updates:
            update_dict = {
                "update_id": update.update_id,
                "message": None,
                "edited_message": None,
                "channel_post": None,
                "edited_channel_post": None,
                "inline_query": None,
                "chosen_inline_result": None,
                "callback_query": None,
                "shipping_query": None,
                "pre_checkout_query": None,
                "poll": None,
                "poll_answer": None,
                "my_chat_member": None,
                "chat_member": None,
                "chat_join_request": None
            }
            
            if update.message:
                update_dict["message"] = {
                    "message_id": update.message.message_id,
                    "date": update.message.date.isoformat(),
                    "chat": {
                        "id": update.message.chat.id,
                        "type": update.message.chat.type,
                        "title": update.message.chat.title,
                        "username": update.message.chat.username
                    },
                    "from": {
                        "id": update.message.from_user.id,
                        "is_bot": update.message.from_user.is_bot,
                        "first_name": update.message.from_user.first_name,
                        "username": update.message.from_user.username
                    } if update.message.from_user else None,
                    "text": update.message.text
                }
            
            updates_data.append(update_dict)
        
        return create_jsonrpc_response({
            "updates": updates_data,
            "count": len(updates_data)
        })
        
    except Exception as e:
        logger.error(f"Ошибка получения обновлений: {e}")
        return create_jsonrpc_error(
            JSONRPCErrorCodes.INTERNAL_ERROR,
            f"Internal error: {str(e)}"
        )

# Обработчик для маршрутизации Telegram инструментов
async def handle_telegram_tool(tool_name: str, params: Dict[str, Any], user_id: str, db: Session) -> Dict[str, Any]:
    """Обработчик для всех Telegram инструментов"""
    try:
        if tool_name not in tools_map:
            return create_jsonrpc_error(
                JSONRPCErrorCodes.METHOD_NOT_FOUND,
                f"Tool {tool_name} not found"
            )
        
        method_name = tools_map[tool_name]
        
        # Вызываем соответствующий метод
        if method_name == "create_bot":
            return await create_bot(params, user_id, db)
        elif method_name == "send_message":
            return await send_message(params, user_id, db)
        elif method_name == "send_photo":
            return await send_photo(params, user_id, db)
        elif method_name == "set_webhook":
            return await set_webhook(params, user_id, db)
        elif method_name == "get_bot_info":
            return await get_bot_info(params, user_id, db)
        elif method_name == "get_updates":
            return await get_updates(params, user_id, db)
        else:
            # Для остальных методов возвращаем заглушку
            return create_jsonrpc_response({
                "message": f"Method {method_name} is not implemented yet",
                "status": "not_implemented"
            })
            
    except Exception as e:
        logger.error(f"Ошибка обработки Telegram инструмента {tool_name}: {e}")
        return create_jsonrpc_error(
            JSONRPCErrorCodes.INTERNAL_ERROR,
            f"Internal error: {str(e)}"
        )