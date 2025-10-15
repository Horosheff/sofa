#!/bin/bash

# 🔍 ПРОВЕРКА ТОКЕНА TELEGRAM БОТА В БАЗЕ ДАННЫХ
echo "🔍 ПРОВЕРЯЕМ ТОКЕН TELEGRAM БОТА В БАЗЕ ДАННЫХ"
echo "=============================================="

# Переходим в папку backend
cd /opt/sofiya/backend

# Проверяем структуру таблицы user_settings
echo "1️⃣ Структура таблицы user_settings:"
sqlite3 app.db ".schema user_settings"

echo ""
echo "2️⃣ Проверяем все записи в user_settings:"
sqlite3 app.db "SELECT user_id, telegram_bot_token, telegram_webhook_url, telegram_webhook_secret FROM user_settings;"

echo ""
echo "3️⃣ Проверяем конкретного пользователя (mr.rutra@gmail.com):"
sqlite3 app.db "SELECT u.email, us.telegram_bot_token, us.telegram_webhook_url, us.telegram_webhook_secret FROM users u JOIN user_settings us ON u.id = us.user_id WHERE u.email = 'mr.rutra@gmail.com';"

echo ""
echo "4️⃣ Проверяем есть ли вообще токены Telegram:"
sqlite3 app.db "SELECT COUNT(*) as telegram_tokens_count FROM user_settings WHERE telegram_bot_token IS NOT NULL AND telegram_bot_token != '';"

echo ""
echo "5️⃣ Показываем первые 50 символов токенов (для безопасности):"
sqlite3 app.db "SELECT user_id, substr(telegram_bot_token, 1, 50) as token_preview FROM user_settings WHERE telegram_bot_token IS NOT NULL AND telegram_bot_token != '';"

echo ""
echo "✅ ПРОВЕРКА ЗАВЕРШЕНА!"
echo "📋 Если токен есть - он должен отображаться выше"
echo "❌ Если токен пустой - нужно добавить токен бота в настройках"
