#!/bin/bash
# 🔍 Проверка логов backend после PUT запроса

echo "🔍 ПРОВЕРКА ЛОГОВ BACKEND..."
echo ""

echo "1️⃣ Поиск SUPER_FINAL_TOKEN_999 в error логах:"
grep "SUPER_FINAL_TOKEN_999" /root/.pm2/logs/backend-error.log | tail -10
echo ""

echo "2️⃣ Поиск PUT /user/settings в error логах:"
grep "PUT /user/settings" /root/.pm2/logs/backend-error.log | tail -5
echo ""

echo "3️⃣ Последние 20 строк error логов:"
tail -20 /root/.pm2/logs/backend-error.log
echo ""

echo "4️⃣ Проверка БД (наличие telegram_bot_token для user_id=1):"
sqlite3 /opt/sofiya/backend/app.db "SELECT id, user_id, telegram_bot_token, telegram_webhook_url FROM user_settings WHERE user_id=1;"
echo ""

echo "✅ ГОТОВО!"

