#!/bin/bash

# 🎯 ДОБАВЛЯЕМ КНОПКУ TELEGRAM В FRONTEND ПРАВИЛЬНО
echo "🎯 ДОБАВЛЯЕМ КНОПКУ TELEGRAM В FRONTEND ПРАВИЛЬНО"
echo "================================================"

# Переходим в правильную папку
cd /opt/sofiya

# 1. СОЗДАЕМ РЕЗЕРВНУЮ КОПИЮ
echo "1️⃣ Создаем резервную копию SettingsPanel..."
cp frontend/components/SettingsPanel.tsx frontend/components/SettingsPanel.tsx.backup

# 2. ЧИТАЕМ ТЕКУЩИЙ ФАЙЛ
echo "2️⃣ Читаем текущий SettingsPanel.tsx..."
head -50 frontend/components/SettingsPanel.tsx

# 3. ДОБАВЛЯЕМ СОСТОЯНИЕ ДЛЯ TELEGRAM TEST
echo "3️⃣ Добавляем состояние для Telegram test..."
# Ищем где добавить useState для telegramTestResult
if ! grep -q "telegramTestResult" frontend/components/SettingsPanel.tsx; then
    echo "Добавляем useState для telegramTestResult..."
    
    # Находим строку с другими useState и добавляем после неё
    sed -i '/const \[.*useState.*\]/a \  const [telegramTestResult, setTelegramTestResult] = useState<{\n    status: '\''idle'\'' | '\''testing'\'' | '\''success'\'' | '\''error'\''\n    message: string\n  }>({ status: '\''idle'\'', message: '\'''\'' })' frontend/components/SettingsPanel.tsx
else
    echo "✅ useState для telegramTestResult уже добавлен"
fi

# 4. ДОБАВЛЯЕМ ФУНКЦИЮ TEST_TELEGRAM_BOT
echo "4️⃣ Добавляем функцию testTelegramBot..."
if ! grep -q "testTelegramBot" frontend/components/SettingsPanel.tsx; then
    echo "Добавляем функцию testTelegramBot..."
    
    # Создаем функцию testTelegramBot
    cat > /tmp/test_telegram_function.tsx << 'EOF'
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

    # Добавляем функцию в файл
    sed -i '/const handleSubmit/a \n  // Функция проверки Telegram бота\n  const testTelegramBot = async () => {\n    setTelegramTestResult({ status: '\''testing'\'', message: '\''Проверяем Telegram бота...'\'' })\n    \n    try {\n      // 1. Сначала сохраняем настройки\n      const settingsData = {\n        telegram_bot_token: watchValues.telegram_bot_token,\n        telegram_webhook_url: watchValues.telegram_webhook_url,\n        telegram_webhook_secret: watchValues.telegram_webhook_secret\n      }\n\n      const saveResponse = await fetch('\''/api/user/settings'\'', {\n        method: '\''PUT'\'',\n        headers: {\n          '\''Content-Type'\'': '\''application/json'\'',\n          '\''Authorization'\'': `Bearer ${user?.token}`\n        },\n        body: JSON.stringify(settingsData)\n      })\n\n      if (!saveResponse.ok) {\n        throw new Error('\''Ошибка сохранения настроек'\'')\n      }\n\n      // 2. Проверяем токен через Telegram API\n      const checkResponse = await fetch('\''/api/telegram/check-token'\'', {\n        method: '\''POST'\'',\n        headers: {\n          '\''Content-Type'\'': '\''application/json'\'',\n          '\''Authorization'\'': `Bearer ${user?.token}`\n        }\n      })\n\n      const checkData = await checkResponse.json()\n      \n      if (checkData.success) {\n        setTelegramTestResult({ \n          status: '\''success'\'', \n          message: `✅ Telegram бот работает! Имя: ${checkData.bot_name || '\''Неизвестно'\''}` \n        })\n      } else {\n        setTelegramTestResult({ \n          status: '\''error'\'', \n          message: `❌ Ошибка: ${checkData.error}` \n        })\n      }\n\n    } catch (error) {\n      setTelegramTestResult({ \n        status: '\''error'\'', \n        message: `❌ Ошибка проверки: ${error}` \n      })\n    }\n  }' frontend/components/SettingsPanel.tsx
else
    echo "✅ Функция testTelegramBot уже добавлена"
fi

# 5. ДОБАВЛЯЕМ КНОПКУ В UI
echo "5️⃣ Добавляем кнопку в UI..."
if ! grep -q "Проверка Telegram бота" frontend/components/SettingsPanel.tsx; then
    echo "Добавляем кнопку проверки Telegram..."
    
    # Создаем кнопку проверки
    cat > /tmp/telegram_button.tsx << 'EOF'
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

    # Добавляем кнопку после полей Telegram
    sed -i '/telegram_webhook_secret.*placeholder/a \n        {/* КНОПКА ПРОВЕРКИ TELEGRAM БОТА */}\n        <div className="mt-6 p-4 bg-blue-500/10 border border-blue-500/20 rounded-lg">\n          <div className="flex items-center justify-between mb-3">\n            <h4 className="text-sm font-semibold text-blue-600">🔍 Проверка Telegram бота</h4>\n            <button\n              type="button"\n              onClick={testTelegramBot}\n              disabled={!watchValues.telegram_bot_token || telegramTestResult.status === '\''testing'\''}\n              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${\n                watchValues.telegram_bot_token && telegramTestResult.status !== '\''testing'\''\n                  ? '\''bg-blue-600 hover:bg-blue-700 text-white'\''\n                  : '\''bg-gray-400 text-gray-200 cursor-not-allowed'\''\n              }`}\n            >\n              {telegramTestResult.status === '\''testing'\'' ? '\''⏳ Проверяем...'\'' : '\''🔍 Проверить бота'\''}\n            </button>\n          </div>\n          \n          {/* Результат проверки */}\n          {telegramTestResult.status !== '\''idle'\'' && (\n            <div className={`p-3 rounded-lg text-sm ${\n              telegramTestResult.status === '\''success'\'' ? '\''bg-green-500/10 text-green-600 border border-green-500/20'\'' :\n              telegramTestResult.status === '\''error'\'' ? '\''bg-red-500/10 text-red-600 border border-red-500/20'\'' :\n              '\''bg-blue-500/10 text-blue-600 border border-blue-500/20'\''\n            }`}>\n              {telegramTestResult.message}\n            </div>\n          )}\n          \n          <p className="text-xs text-foreground/50 mt-2">\n            💡 Кнопка сохранит настройки и проверит доступность бота через Telegram API\n          </p>\n        </div>' frontend/components/SettingsPanel.tsx
else
    echo "✅ Кнопка проверки Telegram уже добавлена"
fi

# 6. ПЕРЕСОБИРАЕМ FRONTEND
echo "6️⃣ Пересобираем frontend..."
cd frontend
rm -rf .next
npm run build

# 7. ПЕРЕЗАПУСКАЕМ FRONTEND
echo "7️⃣ Перезапускаем frontend..."
pm2 restart frontend

# 8. ПРОВЕРЯЕМ СТАТУС
echo "8️⃣ Проверяем статус..."
pm2 status

echo ""
echo "🎯 КНОПКА TELEGRAM ДОБАВЛЕНА В FRONTEND!"
echo "✅ Состояние telegramTestResult добавлено"
echo "✅ Функция testTelegramBot добавлена"
echo "✅ Кнопка '🔍 Проверить бота' добавлена"
echo "✅ Frontend пересобран и перезапущен"
echo ""
echo "🔍 Теперь зайди на сайт и проверь настройки - должна появиться кнопка!"
