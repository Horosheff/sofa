#!/bin/bash

# 🔘 ДОБАВЛЕНИЕ КНОПКИ ПРОВЕРКИ TELEGRAM ТОКЕНА
echo "🔘 ДОБАВЛЕНИЕ КНОПКИ ПРОВЕРКИ TELEGRAM ТОКЕНА"
echo "=============================================="

cd /opt/sofiya/frontend/components

# 1. СОЗДАЕМ БЭКАП
echo "1️⃣ Создаем бэкап SettingsPanel.tsx..."
cp SettingsPanel.tsx SettingsPanel.tsx.backup_$(date +%Y%m%d_%H%M%S)

# 2. ДОБАВЛЯЕМ STATE ДЛЯ КНОПКИ
echo "2️⃣ Добавляем state для кнопки..."
# Находим строку с useState и добавляем новый state после нее
sed -i "/const \[showCodeInput, setShowCodeInput\] = useState(false)/a\\  const [telegramTestResult, setTelegramTestResult] = useState('')\\n  const [isTelegramTesting, setIsTelegramTesting] = useState(false)" SettingsPanel.tsx

# 3. ДОБАВЛЯЕМ ФУНКЦИЮ ПРОВЕРКИ ТОКЕНА
echo "3️⃣ Добавляем функцию проверки токена..."
# Находим строку с handleSubmit и добавляем функцию перед ней
python3 << 'PYTHON_SCRIPT'
with open('SettingsPanel.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# Находим место для вставки функции (перед onSubmit)
insert_marker = '  const onSubmit = async'
if insert_marker in content:
    test_function = '''
  const testTelegramBot = async () => {
    if (!token) {
      error('Необходима авторизация')
      return
    }
    
    setIsTelegramTesting(true)
    setTelegramTestResult('')
    
    try {
      const response = await fetch('/api/telegram/check-token', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      })
      
      const data = await response.json()
      
      if (response.ok) {
        setTelegramTestResult(`✅ Токен валиден! Бот: @${data.bot_info.username}`)
        success('Telegram бот успешно подключен!')
      } else {
        setTelegramTestResult(`❌ Ошибка: ${data.detail}`)
        error('Ошибка проверки токена')
      }
    } catch (err) {
      console.error('Ошибка проверки Telegram токена:', err)
      setTelegramTestResult('❌ Ошибка соединения с сервером')
      error('Ошибка проверки токена')
    } finally {
      setIsTelegramTesting(false)
    }
  }

'''
    content = content.replace(insert_marker, test_function + insert_marker)
    
    with open('SettingsPanel.tsx', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Функция добавлена")
else:
    print("❌ Не найдено место для вставки функции")
    exit(1)
PYTHON_SCRIPT

# 4. ДОБАВЛЯЕМ КНОПКУ В JSX
echo "4️⃣ Добавляем кнопку в JSX..."
python3 << 'PYTHON_SCRIPT'
with open('SettingsPanel.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# Находим место для вставки кнопки (после последнего PasswordField в Telegram секции)
insert_marker = '''            <PasswordField
              label="Webhook Secret (опционально)"
              name="telegram_webhook_secret"
              value={watchValues.telegram_webhook_secret}
              onChange={(value) => setValue('telegram_webhook_secret', value, { shouldDirty: true })}
              placeholder="your-secret-key"
            />
          </div>'''

if insert_marker in content:
    button_code = '''            <PasswordField
              label="Webhook Secret (опционально)"
              name="telegram_webhook_secret"
              value={watchValues.telegram_webhook_secret}
              onChange={(value) => setValue('telegram_webhook_secret', value, { shouldDirty: true })}
              placeholder="your-secret-key"
            />
          </div>
          
          {/* Кнопка проверки токена */}
          <div className="mt-4">
            <button
              type="button"
              onClick={testTelegramBot}
              disabled={!watchValues.telegram_bot_token || isTelegramTesting}
              className="modern-btn w-full md:w-auto disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isTelegramTesting ? '⏳ Проверка...' : '🔍 Проверить токен бота'}
            </button>
            {telegramTestResult && (
              <p className="mt-2 text-sm text-foreground/70">{telegramTestResult}</p>
            )}
          </div>'''
    
    content = content.replace(insert_marker, button_code)
    
    with open('SettingsPanel.tsx', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Кнопка добавлена")
else:
    print("❌ Не найдено место для вставки кнопки")
    exit(1)
PYTHON_SCRIPT

# 5. ПРОВЕРЯЕМ ЧТО КНОПКА ДОБАВЛЕНА
echo "5️⃣ Проверяем что кнопка добавлена..."
if grep -q "Проверить токен бота" SettingsPanel.tsx; then
    echo "✅ Кнопка успешно добавлена"
else
    echo "❌ Кнопка не добавлена"
    exit 1
fi

# 6. ПЕРЕСОБИРАЕМ FRONTEND
echo "6️⃣ Пересобираем frontend..."
cd /opt/sofiya/frontend
rm -rf .next/
npm run build

# 7. ПЕРЕЗАПУСКАЕМ FRONTEND
echo "7️⃣ Перезапускаем frontend..."
cd /opt/sofiya
pm2 restart frontend

# 8. ПРОВЕРЯЕМ СТАТУС
echo "8️⃣ Проверяем статус..."
pm2 status

echo ""
echo "🎯 КНОПКА ПРОВЕРКИ TELEGRAM ТОКЕНА ДОБАВЛЕНА!"
echo "✅ State добавлен"
echo "✅ Функция testTelegramBot добавлена"
echo "✅ Кнопка добавлена в JSX"
echo "✅ Frontend пересобран и перезапущен"
echo ""
echo "Теперь зайди в настройки и увидишь кнопку 'Проверить токен бота'!"
