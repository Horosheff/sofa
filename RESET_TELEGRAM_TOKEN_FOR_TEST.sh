#!/bin/bash

# 🗑️ СБРОС TELEGRAM ТОКЕНА ДЛЯ ТЕСТИРОВАНИЯ
echo "🗑️ СБРОС TELEGRAM ТОКЕНА ДЛЯ ТЕСТИРОВАНИЯ"
echo "=========================================="

cd /opt/sofiya/backend

# 1. ПОКАЗЫВАЕМ ТЕКУЩЕЕ СОСТОЯНИЕ
echo "1️⃣ Текущее состояние токена:"
sqlite3 app.db << 'SQL'
.mode column
.headers on
SELECT 
    u.email,
    CASE 
        WHEN us.telegram_bot_token IS NOT NULL THEN '✅ Есть токен'
        ELSE '❌ Нет токена'
    END as status,
    LENGTH(us.telegram_bot_token) as token_length
FROM user_settings us
JOIN users u ON us.user_id = u.id
WHERE u.email = 'mr.rutra@gmail.com';
SQL

# 2. УДАЛЯЕМ ТОКЕН
echo ""
echo "2️⃣ Удаляем токен из базы данных..."
sqlite3 app.db << 'SQL'
UPDATE user_settings 
SET telegram_bot_token = NULL,
    telegram_webhook_url = NULL,
    telegram_webhook_secret = NULL
WHERE user_id = (SELECT id FROM users WHERE email = 'mr.rutra@gmail.com');
SQL

echo "✅ Токен удален"

# 3. ПРОВЕРЯЕМ ЧТО ТОКЕН УДАЛЕН
echo ""
echo "3️⃣ Проверяем что токен удален:"
sqlite3 app.db << 'SQL'
.mode column
.headers on
SELECT 
    u.email,
    CASE 
        WHEN us.telegram_bot_token IS NOT NULL THEN '✅ Есть токен'
        ELSE '❌ Нет токена'
    END as status
FROM user_settings us
JOIN users u ON us.user_id = u.id
WHERE u.email = 'mr.rutra@gmail.com';
SQL

echo ""
echo "🎯 ТОКЕН УДАЛЕН ДЛЯ ТЕСТИРОВАНИЯ!"
echo "✅ База данных очищена"
echo "✅ Теперь можно протестировать:"
echo "   1. Ввод нового токена"
echo "   2. Проверку с автосохранением"
echo "   3. Шифрование при сохранении"
echo ""
echo "Зайди на сайт и введи токен заново!"
