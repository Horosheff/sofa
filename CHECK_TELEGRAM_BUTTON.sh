#!/bin/bash

# 🔍 ПРОВЕРКА TELEGRAM КНОПКИ
echo "🔍 ПРОВЕРКА TELEGRAM КНОПКИ"
echo "==========================="

cd /opt/sofiya

# 1. ПРОВЕРЯЕМ НАСТРОЙКИ ПОЛЬЗОВАТЕЛЯ В БД
echo "1️⃣ Проверяем настройки пользователя в БД..."
cd backend
sqlite3 app.db << 'SQL'
.mode column
.headers on
SELECT 
    id,
    user_id,
    telegram_bot_token IS NOT NULL as has_telegram_token,
    telegram_webhook_url,
    LENGTH(telegram_bot_token) as token_length
FROM user_settings;
SQL

# 2. ПРОВЕРЯЕМ API /user/settings
echo ""
echo "2️⃣ Проверяем что возвращает API /user/settings..."
echo "Зайди на сайт, открой DevTools (F12), вкладка Network, обнови страницу настроек"
echo "и найди запрос к /user/settings. Покажи мне ответ."
echo ""
echo "Или выполни на сервере:"
echo 'curl -s https://mcp-kv.ru/api/user/settings -H "Authorization: Bearer YOUR_TOKEN"'
echo ""

# 3. ПРОВЕРЯЕМ ЕСТЬ ЛИ КНОПКА В SETTINGSPANEL.TSX
echo "3️⃣ Проверяем есть ли кнопка в SettingsPanel.tsx..."
cd /opt/sofiya/frontend/components
if grep -q "Check Telegram Bot" SettingsPanel.tsx; then
    echo "✅ Кнопка 'Check Telegram Bot' НАЙДЕНА в SettingsPanel.tsx"
    echo ""
    echo "Контекст кнопки:"
    grep -B 5 -A 5 "Check Telegram Bot" SettingsPanel.tsx
else
    echo "❌ Кнопка 'Check Telegram Bot' НЕ НАЙДЕНА в SettingsPanel.tsx"
    echo ""
    echo "Нужно добавить кнопку!"
fi

# 4. ПРОВЕРЯЕМ ЕСТЬ ЛИ TELEGRAM_CHECK.PY
echo ""
echo "4️⃣ Проверяем есть ли backend endpoint..."
cd /opt/sofiya/backend/app
if [ -f "telegram_check.py" ]; then
    echo "✅ telegram_check.py НАЙДЕН"
    head -20 telegram_check.py
else
    echo "❌ telegram_check.py НЕ НАЙДЕН"
    echo "Нужно создать файл!"
fi

# 5. ПРОВЕРЯЕМ ПОДКЛЮЧЕН ЛИ РОУТЕР В MAIN.PY
echo ""
echo "5️⃣ Проверяем подключен ли telegram_check роутер в main.py..."
if grep -q "telegram_check_router" main.py; then
    echo "✅ telegram_check_router НАЙДЕН в main.py"
    grep -n "telegram_check_router" main.py
else
    echo "❌ telegram_check_router НЕ НАЙДЕН в main.py"
    echo "Нужно добавить импорт и подключить роутер!"
fi

echo ""
echo "🎯 ПРОВЕРКА ЗАВЕРШЕНА!"
echo ""
echo "Теперь я знаю что нужно исправить!"
