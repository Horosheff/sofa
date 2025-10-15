from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user
from app.models import UserSettings
from app.helpers import decrypt_token
from telegram import Bot
import asyncio

router = APIRouter()

@router.post("/check-token")
async def check_telegram_token(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Проверить токен Telegram бота
    """
    try:
        # Получаем настройки пользователя
        settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
        
        if not settings or not settings.telegram_bot_token:
            raise HTTPException(status_code=400, detail="Telegram bot token не настроен")
        
        # Расшифровываем токен
        try:
            bot_token = decrypt_token(settings.telegram_bot_token)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Ошибка расшифровки токена: {str(e)}")
        
        # Проверяем токен через Telegram API
        try:
            bot = Bot(token=bot_token)
            bot_info = await bot.get_me()
            
            return {
                "success": True,
                "bot_name": bot_info.first_name,
                "bot_username": bot_info.username,
                "bot_id": bot_info.id,
                "message": f"✅ Бот '{bot_info.first_name}' (@{bot_info.username}) работает!"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Ошибка Telegram API: {str(e)}",
                "message": "❌ Неверный токен или проблемы с Telegram API"
            }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка: {str(e)}")
