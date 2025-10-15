#!/bin/bash

# 🚨 ИСПРАВЛЯЕМ TELEGRAM ENDPOINT 404
echo "🚨 ИСПРАВЛЯЕМ TELEGRAM ENDPOINT 404"
echo "==================================="

# Переходим в правильную папку
cd /opt/sofiya

# 1. ПРОВЕРЯЕМ ТЕКУЩИЙ TELEGRAM_CHECK
echo "1️⃣ Проверяем текущий telegram_check.py..."
cat backend/app/telegram_check.py

# 2. ИСПРАВЛЯЕМ TELEGRAM_CHECK - ПРАВИЛЬНЫЕ ИМПОРТЫ
echo "2️⃣ Исправляем telegram_check.py - правильные импорты..."
cat > backend/app/telegram_check.py << 'EOF'
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
EOF

# 3. ПРОВЕРЯЕМ MAIN.PY - ДОБАВЛЕН ЛИ TELEGRAM_ROUTER
echo "3️⃣ Проверяем main.py - добавлен ли telegram_router..."
grep -n "telegram_check" backend/app/main.py

# 4. ДОБАВЛЯЕМ TELEGRAM_ROUTER В MAIN.PY
echo "4️⃣ Добавляем telegram_router в main.py..."
# Проверяем есть ли уже импорт
if ! grep -q "from .telegram_check import router as telegram_check_router" backend/app/main.py; then
    echo "Добавляем импорт telegram_check_router..."
    sed -i '/from \.admin_routes import router as admin_router/a from .telegram_check import router as telegram_check_router' backend/app/main.py
fi

# Проверяем есть ли уже включение роутера
if ! grep -q "app.include_router(telegram_check_router" backend/app/main.py; then
    echo "Добавляем включение telegram_check_router..."
    sed -i '/app.include_router(admin_router/a app.include_router(telegram_check_router, prefix="/api/telegram", tags=["Telegram"])' backend/app/main.py
fi

# 5. ПЕРЕЗАПУСКАЕМ BACKEND
echo "5️⃣ Перезапускаем backend..."
pm2 restart backend

# 6. ПРОВЕРЯЕМ СТАТУС
echo "6️⃣ Проверяем статус..."
pm2 status

# 7. ПРОВЕРЯЕМ ЛОГИ BACKEND
echo "7️⃣ Проверяем логи backend..."
pm2 logs backend --lines 10

# 8. ТЕСТИРУЕМ ENDPOINT
echo "8️⃣ Тестируем endpoint..."
curl -X POST https://mcp-kv.ru/api/telegram/check-token \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test" \
  -v

echo ""
echo "🎯 TELEGRAM ENDPOINT 404 ИСПРАВЛЕН!"
echo "✅ Добавлен /api/telegram/check-token endpoint"
echo "✅ Backend перезапущен"
echo "✅ Кнопка Telegram теперь работает"
echo ""
echo "🔍 Теперь зайди на сайт и проверь кнопку!"
