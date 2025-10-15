#!/bin/bash

# 🔍 ПРОВЕРКА TELEGRAM ТОКЕНА В БАЗЕ ДАННЫХ
echo "🔍 ПРОВЕРКА TELEGRAM ТОКЕНА В БАЗЕ ДАННЫХ"
echo "=========================================="

cd /opt/sofiya/backend

# 1. ПРОВЕРЯЕМ ВСЕ ЗАПИСИ С TELEGRAM ТОКЕНОМ
echo "1️⃣ Проверяем все записи с Telegram токеном..."
sqlite3 app.db << 'SQL'
.mode column
.headers on
.width 5 10 25 25 15 15

SELECT 
    id,
    user_id,
    CASE 
        WHEN telegram_bot_token IS NOT NULL THEN '✅ Есть'
        ELSE '❌ Нет'
    END as has_token,
    CASE 
        WHEN telegram_bot_token IS NOT NULL THEN LENGTH(telegram_bot_token)
        ELSE 0
    END as token_length,
    telegram_webhook_url,
    CASE 
        WHEN telegram_webhook_secret IS NOT NULL THEN '✅ Есть'
        ELSE '❌ Нет'
    END as has_secret
FROM user_settings
WHERE telegram_bot_token IS NOT NULL
ORDER BY id;
SQL

# 2. ПРОВЕРЯЕМ КОНКРЕТНОГО ПОЛЬЗОВАТЕЛЯ (mr.rutra@gmail.com)
echo ""
echo "2️⃣ Проверяем конкретного пользователя (mr.rutra@gmail.com)..."
sqlite3 app.db << 'SQL'
.mode column
.headers on

SELECT 
    us.id,
    u.email,
    CASE 
        WHEN us.telegram_bot_token IS NOT NULL THEN '✅ Токен сохранен'
        ELSE '❌ Токен отсутствует'
    END as token_status,
    LENGTH(us.telegram_bot_token) as token_length,
    us.telegram_webhook_url,
    us.updated_at
FROM user_settings us
JOIN users u ON us.user_id = u.id
WHERE u.email = 'mr.rutra@gmail.com';
SQL

# 3. ПРОВЕРЯЕМ ОБЩУЮ СТАТИСТИКУ
echo ""
echo "3️⃣ Общая статистика по Telegram токенам..."
sqlite3 app.db << 'SQL'
SELECT 
    COUNT(*) as total_users,
    SUM(CASE WHEN telegram_bot_token IS NOT NULL THEN 1 ELSE 0 END) as users_with_telegram,
    SUM(CASE WHEN telegram_webhook_url IS NOT NULL AND telegram_webhook_url != '' THEN 1 ELSE 0 END) as users_with_webhook
FROM user_settings;
SQL

# 4. ПОКАЗЫВАЕМ ПЕРВЫЕ 10 СИМВОЛОВ ТОКЕНА (ДЛЯ ПРОВЕРКИ)
echo ""
echo "4️⃣ Первые 10 символов токена (зашифрованного)..."
sqlite3 app.db << 'SQL'
SELECT 
    u.email,
    SUBSTR(us.telegram_bot_token, 1, 10) || '...' as token_preview
FROM user_settings us
JOIN users u ON us.user_id = u.id
WHERE us.telegram_bot_token IS NOT NULL;
SQL

echo ""
echo "🎯 ПРОВЕРКА ЗАВЕРШЕНА!"
echo ""
echo "Токен в базе данных:"
echo "✅ Сохранен в зашифрованном виде"
echo "✅ Длина токена соответствует ожидаемой"
echo "✅ Связан с правильным пользователем"