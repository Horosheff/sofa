#!/bin/bash

echo "🔍 Проверяем последний PUT /user/settings request body..."

# Найти последний запрос в error.log (там более детальные логи)
grep -A 20 ">>> REQUEST: PUT /user/settings" /root/.pm2/logs/backend-error.log | tail -50 | grep -A 5 "Body:"

echo ""
echo "📊 Проверяем БД - есть ли telegram_bot_token:"
sqlite3 /opt/sofiya/backend/app.db "SELECT user_id, LENGTH(telegram_bot_token) as token_length, telegram_bot_token FROM user_settings WHERE user_id = 1;"

echo ""
echo "✅ Готово!"

