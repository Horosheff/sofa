#!/bin/bash

# 🗑️ ОЧИСТКА СТАРОГО TELEGRAM ТОКЕНА
echo "🗑️ ОЧИСТКА СТАРОГО TELEGRAM ТОКЕНА"
echo "===================================="

cd /opt/sofiya/backend

# 1. ПОКАЗЫВАЕМ ТЕКУЩИЙ ТОКЕН
echo "1️⃣ Текущий токен в базе данных:"
sqlite3 app.db << 'SQL'
SELECT 
    us.id,
    u.email,
    CASE 
        WHEN us.telegram_bot_token IS NOT NULL THEN '✅ Есть токен'
        ELSE '❌ Нет токена'
    END as status,
    LENGTH(us.telegram_bot_token) as token_length,
    SUBSTR(us.telegram_bot_token, 1, 20) || '...' as token_preview
FROM user_settings us
JOIN users u ON us.user_id = u.id
WHERE u.email = 'mr.rutra@gmail.com';
SQL

# 2. УДАЛЯЕМ СТАРЫЙ ТОКЕН
echo ""
echo "2️⃣ Удаляем старый токен (зашифрованный временным ключом)..."
sqlite3 app.db << 'SQL'
UPDATE user_settings 
SET telegram_bot_token = NULL,
    telegram_webhook_url = NULL,
    telegram_webhook_secret = NULL
WHERE user_id = (SELECT id FROM users WHERE email = 'mr.rutra@gmail.com');
SQL

echo "✅ Старый токен удален"

# 3. ПРОВЕРЯЕМ ЧТО ТОКЕН УДАЛЕН
echo ""
echo "3️⃣ Проверяем что токен удален:"
sqlite3 app.db << 'SQL'
SELECT 
    us.id,
    u.email,
    CASE 
        WHEN us.telegram_bot_token IS NOT NULL THEN '✅ Есть токен'
        ELSE '❌ Нет токена'
    END as status
FROM user_settings us
JOIN users u ON us.user_id = u.id
WHERE u.email = 'mr.rutra@gmail.com';
SQL

# 4. ПЕРЕЗАПУСКАЕМ BACKEND
echo ""
echo "4️⃣ Перезапускаем backend..."
cd /opt/sofiya
pm2 restart backend

# 5. ПРОВЕРЯЕМ СТАТУС
echo ""
echo "5️⃣ Проверяем статус..."
sleep 3
pm2 status

echo ""
echo "🎯 СТАРЫЙ ТОКЕН УДАЛЕН!"
echo "✅ Токен удален из базы данных"
echo "✅ Backend перезапущен"
echo ""
echo "📋 СЛЕДУЮЩИЕ ШАГИ:"
echo "1. Зайди на сайт в настройки"
echo "2. Введи токен Telegram бота ЗАНОВО"
echo "3. Нажми 'Сохранить'"
echo "4. Нажми кнопку '🔍 Проверить токен бота'"
echo ""
echo "Токен будет зашифрован НОВЫМ постоянным ключом!"
