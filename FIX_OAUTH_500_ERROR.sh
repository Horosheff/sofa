#!/bin/bash

# 🚨 ЭКСТРЕННЫЙ ПАТЧ ДЛЯ ИСПРАВЛЕНИЯ OAUTH 500 ERROR
# Проблема: 500 Internal Server Error при получении токена WordPress

echo "🚨 ЭКСТРЕННЫЙ ПАТЧ ДЛЯ ИСПРАВЛЕНИЯ OAUTH 500 ERROR"
echo "=================================================="

# 1. ПРОВЕРЯЕМ СТАТУС СЕРВИСОВ
echo "1️⃣ Проверяем статус сервисов..."
pm2 status

# 2. ПРОВЕРЯЕМ ЛОГИ BACKEND
echo "2️⃣ Проверяем логи backend..."
pm2 logs backend --lines 20

# 3. ПЕРЕЗАПУСКАЕМ BACKEND
echo "3️⃣ Перезапускаем backend..."
pm2 restart backend

# 4. ЖДЕМ 5 СЕКУНД
echo "4️⃣ Ждем 5 секунд..."
sleep 5

# 5. ПРОВЕРЯЕМ СТАТУС
echo "5️⃣ Проверяем статус после перезапуска..."
pm2 status

# 6. ТЕСТИРУЕМ API
echo "6️⃣ Тестируем API..."
curl -I https://mcp-kv.ru/api/mcp/tools

# 7. ПРОВЕРЯЕМ ЛОГИ ПОСЛЕ ПЕРЕЗАПУСКА
echo "7️⃣ Проверяем логи после перезапуска..."
pm2 logs backend --lines 10

echo ""
echo "🎯 ПАТЧ ЗАВЕРШЕН!"
echo "✅ Backend перезапущен"
echo "✅ API протестирован"
echo ""
echo "🔍 Теперь попробуйте снова получить токен WordPress"
echo "📋 Если проблема остается, проверьте логи: pm2 logs backend"
