#!/bin/bash

# 🚨 ИСПРАВЛЯЕМ ОШИБКУ ИМПОРТА В TELEGRAM_CHECK.PY
echo "🚨 ИСПРАВЛЯЕМ ОШИБКУ ИМПОРТА В TELEGRAM_CHECK.PY"
echo "================================================"

# Переходим в правильную папку
cd /opt/sofiya

# 1. ИСПРАВЛЯЕМ ИМПОРТЫ В TELEGRAM_CHECK.PY
echo "1️⃣ Исправляем импорты в telegram_check.py..."
cat > backend/app/telegram_check.py << 'EOF'
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, UserSettings
from app.auth import get_current_user
import httpx
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/telegram/check-token")
async def check_telegram_token(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Проверить токен Telegram бота"""
    
    try:
        # Получаем настройки пользователя
        settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
        
        if not settings or not settings.telegram_bot_token:
            return {
                "success": False,
                "error": "Токен Telegram бота не найден в настройках"
            }
        
        # Проверяем токен через Telegram API
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.telegram.org/bot{settings.telegram_bot_token}/getMe",
                timeout=10.0
            )
            
            if response.status_code == 200:
                bot_data = response.json()
                if bot_data.get("ok"):
                    return {
                        "success": True,
                        "bot_name": bot_data["result"].get("first_name", "Неизвестно"),
                        "bot_username": bot_data["result"].get("username", ""),
                        "bot_id": bot_data["result"].get("id", ""),
                        "message": "Telegram бот работает корректно"
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Ошибка Telegram API: {bot_data.get('description', 'Неизвестная ошибка')}"
                    }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                
    except httpx.TimeoutException:
        return {
            "success": False,
            "error": "Таймаут при обращении к Telegram API"
        }
    except Exception as e:
        logger.error(f"Ошибка проверки Telegram токена: {e}")
        return {
            "success": False,
            "error": f"Внутренняя ошибка: {str(e)}"
        }
EOF

# 2. ПРОВЕРЯЕМ ЧТО ИМПОРТ ДОБАВЛЕН В MAIN.PY
echo "2️⃣ Проверяем импорт в main.py..."
if grep -q "telegram_check" backend/app/main.py; then
    echo "✅ Импорт telegram_check уже добавлен"
else
    echo "❌ Импорт telegram_check НЕ найден, добавляем..."
    # Добавляем импорт после других импортов
    sed -i '/from \.admin_routes import router as admin_router/a from .telegram_check import router as telegram_check_router' backend/app/main.py
    
    # Добавляем роутер после других роутеров
    sed -i '/app.include_router(admin_router, prefix="\/api", tags=\["admin"\])/a app.include_router(telegram_check_router, prefix="\/api", tags=["telegram-check"])' backend/app/main.py
fi

# 3. ПЕРЕЗАПУСКАЕМ BACKEND
echo "3️⃣ Перезапускаем backend..."
pm2 restart backend

# 4. ЖДЕМ 3 СЕКУНДЫ
echo "4️⃣ Ждем 3 секунды..."
sleep 3

# 5. ПРОВЕРЯЕМ СТАТУС
echo "5️⃣ Проверяем статус..."
pm2 status

# 6. ПРОВЕРЯЕМ ЛОГИ
echo "6️⃣ Проверяем логи backend..."
pm2 logs backend --lines 10

echo ""
echo "🎯 ИСПРАВЛЕНИЕ ЗАВЕРШЕНО!"
echo "✅ Импорты исправлены"
echo "✅ Backend перезапущен"
echo ""
echo "🔍 Проверьте логи выше - не должно быть ошибок импорта"
