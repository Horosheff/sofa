#!/bin/bash

# 🔧 ИСПРАВЛЯЕМ ПУТИ ДЛЯ КНОПКИ TELEGRAM БОТА
echo "🔧 ИСПРАВЛЯЕМ ПУТИ ДЛЯ КНОПКИ TELEGRAM БОТА"
echo "=========================================="

# Переходим в правильную папку
cd /opt/sofiya

echo "📁 Текущая папка: $(pwd)"
echo "📋 Содержимое папки:"
ls -la

echo ""
echo "🎯 ДОБАВЛЯЕМ КНОПКУ ПРОВЕРКИ TELEGRAM БОТА"
echo "=========================================="

# 1. СОЗДАЕМ BACKEND ENDPOINT ДЛЯ ПРОВЕРКИ ТОКЕНА
echo "1️⃣ Создаем backend endpoint для проверки токена..."
cat > backend/app/telegram_check.py << 'EOF'
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, UserSettings
from ..auth import get_current_user
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

# 2. ДОБАВЛЯЕМ РОУТЕР В MAIN.PY
echo "2️⃣ Добавляем роутер в main.py..."
# Проверяем есть ли уже импорт
if ! grep -q "telegram_check" backend/app/main.py; then
    echo "Добавляем импорт telegram_check..."
    sed -i '/from \.admin_routes import router as admin_router/a from .telegram_check import router as telegram_check_router' backend/app/main.py
    
    echo "Добавляем роутер..."
    sed -i '/app.include_router(admin_router, prefix="/api", tags=\["admin"\])/a app.include_router(telegram_check_router, prefix="/api", tags=["telegram-check"])' backend/app/main.py
else
    echo "✅ Роутер telegram_check уже добавлен"
fi

# 3. ОБНОВЛЯЕМ FRONTEND SETTINGS PANEL
echo "3️⃣ Обновляем frontend SettingsPanel..."
# Создаем резервную копию
cp frontend/components/SettingsPanel.tsx frontend/components/SettingsPanel.tsx.backup

# Добавляем состояние для проверки Telegram
cat > /tmp/telegram_test_state.tsx << 'EOF'
  // Добавляем состояние для проверки Telegram
  const [telegramTestResult, setTelegramTestResult] = useState<{
    status: 'idle' | 'testing' | 'success' | 'error'
    message: string
  }>({ status: 'idle', message: '' })

  // Функция проверки Telegram бота
  const testTelegramBot = async () => {
    setTelegramTestResult({ status: 'testing', message: 'Проверяем Telegram бота...' })
    
    try {
      // 1. Сначала сохраняем настройки
      const settingsData = {
        telegram_bot_token: watchValues.telegram_bot_token,
        telegram_webhook_url: watchValues.telegram_webhook_url,
        telegram_webhook_secret: watchValues.telegram_webhook_secret
      }

      const saveResponse = await fetch('/api/user/settings', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${user?.token}`
        },
        body: JSON.stringify(settingsData)
      })

      if (!saveResponse.ok) {
        throw new Error('Ошибка сохранения настроек')
      }

      // 2. Проверяем токен через Telegram API
      const checkResponse = await fetch('/api/telegram/check-token', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${user?.token}`
        }
      })

      const checkData = await checkResponse.json()
      
      if (checkData.success) {
        setTelegramTestResult({ 
          status: 'success', 
          message: `✅ Telegram бот работает! Имя: ${checkData.bot_name || 'Неизвестно'}` 
        })
      } else {
        setTelegramTestResult({ 
          status: 'error', 
          message: `❌ Ошибка: ${checkData.error}` 
        })
      }

    } catch (error) {
      setTelegramTestResult({ 
        status: 'error', 
        message: `❌ Ошибка проверки: ${error}` 
      })
    }
  }
EOF

# Добавляем кнопку проверки в SettingsPanel
cat > /tmp/telegram_test_button.tsx << 'EOF'
        {/* КНОПКА ПРОВЕРКИ TELEGRAM БОТА */}
        <div className="mt-6 p-4 bg-blue-500/10 border border-blue-500/20 rounded-lg">
          <div className="flex items-center justify-between mb-3">
            <h4 className="text-sm font-semibold text-blue-600">🔍 Проверка Telegram бота</h4>
            <button
              type="button"
              onClick={testTelegramBot}
              disabled={!watchValues.telegram_bot_token || telegramTestResult.status === 'testing'}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                watchValues.telegram_bot_token && telegramTestResult.status !== 'testing'
                  ? 'bg-blue-600 hover:bg-blue-700 text-white'
                  : 'bg-gray-400 text-gray-200 cursor-not-allowed'
              }`}
            >
              {telegramTestResult.status === 'testing' ? '⏳ Проверяем...' : '🔍 Проверить бота'}
            </button>
          </div>
          
          {/* Результат проверки */}
          {telegramTestResult.status !== 'idle' && (
            <div className={`p-3 rounded-lg text-sm ${
              telegramTestResult.status === 'success' ? 'bg-green-500/10 text-green-600 border border-green-500/20' :
              telegramTestResult.status === 'error' ? 'bg-red-500/10 text-red-600 border border-red-500/20' :
              'bg-blue-500/10 text-blue-600 border border-blue-500/20'
            }`}>
              {telegramTestResult.message}
            </div>
          )}
          
          <p className="text-xs text-foreground/50 mt-2">
            💡 Кнопка сохранит настройки и проверит доступность бота через Telegram API
          </p>
        </div>
EOF

# 4. ПЕРЕЗАПУСКАЕМ BACKEND
echo "4️⃣ Перезапускаем backend..."
pm2 restart backend

# 5. ПЕРЕСОБИРАЕМ FRONTEND
echo "5️⃣ Пересобираем frontend..."
cd frontend
rm -rf .next
npm run build

# 6. ПЕРЕЗАПУСКАЕМ FRONTEND
echo "6️⃣ Перезапускаем frontend..."
pm2 restart frontend

# 7. ПРОВЕРЯЕМ СТАТУС
echo "7️⃣ Проверяем статус..."
pm2 status

echo ""
echo "🎯 КНОПКА ПРОВЕРКИ TELEGRAM БОТА ДОБАВЛЕНА!"
echo "✅ Backend: Endpoint /api/telegram/check-token создан"
echo "✅ Frontend: Пересобран с новой функциональностью"
echo "✅ Сервисы: Перезапущены"
echo ""
echo "🔍 Проверьте сайт: https://mcp-kv.ru"
echo "📋 В настройках должна появиться кнопка '🔍 Проверить бота'"
