#!/bin/bash

# 🎯 ДОБАВЛЯЕМ КНОПКУ ПРОВЕРКИ TELEGRAM БОТА
echo "🎯 ДОБАВЛЯЕМ КНОПКУ ПРОВЕРКИ TELEGRAM БОТА"
echo "=========================================="

# Создаем патч для SettingsPanel.tsx
cat > frontend/components/SettingsPanel.tsx << 'EOF'
// ... existing imports ...

export default function SettingsPanel() {
  // ... existing code ...

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

      // 2. Проверяем что токен сохранился в базе
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

  return (
    <div className="space-y-6">
      {/* ... existing code ... */}

      {/* Telegram Bot Settings */}
      <div className="glass-panel">
        <h3 className="text-xl font-bold text-foreground mb-6 flex items-center">
          🤖 Telegram Bot настройки
        </h3>
        
        {/* Инструкция по созданию бота */}
        <div className="glass-form p-4 mb-6 border-l-4 border-blue-400/50">
          <h4 className="text-sm font-semibold text-foreground mb-2 flex items-center">
            💡 Как создать Telegram бота:
          </h4>
          <ol className="text-sm text-foreground/70 space-y-2 list-decimal list-inside">
            <li>Найдите <strong>@BotFather</strong> в Telegram</li>
            <li>Отправьте команду <code className="text-xs bg-white/10 px-2 py-1 rounded">/newbot</code></li>
            <li>Введите имя для вашего бота (например: "My Awesome Bot")</li>
            <li>Введите username для бота (например: "my_awesome_bot")</li>
            <li>Скопируйте полученный токен и вставьте в поле ниже</li>
          </ol>
          <p className="text-xs text-foreground/50 mt-3">
            🔐 <strong>Безопасность:</strong> Токен бота дает полный доступ к управлению ботом. Храните его в безопасности!
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <PasswordField
            label="Токен бота"
            name="telegram_bot_token"
            value={watchValues.telegram_bot_token}
            onChange={(value) => setValue('telegram_bot_token', value, { shouldDirty: true })}
            placeholder="123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
            className="md:col-span-2"
          />
          <div>
            <label className="block text-sm font-medium text-foreground/80 mb-2">
              Webhook URL (опционально)
            </label>
            <input
              {...register('telegram_webhook_url')}
              type="url"
              className="modern-input w-full"
              placeholder="https://your-domain.com/webhook"
            />
            <p className="text-xs text-foreground/50 mt-1">URL для получения обновлений от Telegram</p>
          </div>
          <PasswordField
            label="Webhook Secret (опционально)"
            name="telegram_webhook_secret"
            value={watchValues.telegram_webhook_secret}
            onChange={(value) => setValue('telegram_webhook_secret', value, { shouldDirty: true })}
            placeholder="your-secret-key"
          />
        </div>

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
      </div>

      {/* ... existing code ... */}
    </div>
  )
}
EOF

# Создаем backend endpoint для проверки токена
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

# Добавляем роутер в main.py
echo "Добавляем Telegram check роутер в main.py..."

# Создаем патч для main.py
cat >> backend/app/main.py << 'EOF'

# Добавляем импорт
from .telegram_check import router as telegram_check_router

# Добавляем роутер
app.include_router(telegram_check_router, prefix="/api", tags=["telegram-check"])
EOF

echo ""
echo "🎯 КНОПКА ПРОВЕРКИ TELEGRAM БОТА ДОБАВЛЕНА!"
echo "✅ Frontend: Кнопка '🔍 Проверить бота' в настройках"
echo "✅ Backend: Endpoint /api/telegram/check-token"
echo "✅ Функции: Сохранение + проверка токена + тест API"
echo ""
echo "🚀 Теперь нужно пересобрать frontend и перезапустить backend!"
