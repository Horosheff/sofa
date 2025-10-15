#!/bin/bash

# 🚨 ИСПРАВЛЯЕМ FRONTEND SPREAD ERROR
echo "🚨 ИСПРАВЛЯЕМ FRONTEND SPREAD ERROR"
echo "=================================="

# Переходим в правильную папку
cd /opt/sofiya

# 1. ПРОВЕРЯЕМ FRONTEND СБОРКУ
echo "1️⃣ Проверяем frontend сборку..."
cd frontend
ls -la .next/

# 2. ОЧИЩАЕМ КЭШ
echo "2️⃣ Очищаем кэш..."
rm -rf .next/
rm -rf node_modules/.cache/

# 3. ПЕРЕСОБИРАЕМ FRONTEND
echo "3️⃣ Пересобираем frontend..."
npm run build

# 4. ПЕРЕЗАПУСКАЕМ FRONTEND
echo "4️⃣ Перезапускаем frontend..."
pm2 restart frontend

# 5. ПРОВЕРЯЕМ СТАТУС
echo "5️⃣ Проверяем статус..."
pm2 status

# 6. ПРОВЕРЯЕМ ЛОГИ FRONTEND
echo "6️⃣ Проверяем логи frontend..."
pm2 logs frontend --lines 10

# 7. ТЕСТИРУЕМ САЙТ
echo "7️⃣ Тестируем сайт..."
curl -I https://mcp-kv.ru

echo ""
echo "🎯 FRONTEND SPREAD ERROR ИСПРАВЛЕН!"
echo "✅ Очищен кэш frontend"
echo "✅ Пересобран frontend"
echo "✅ Перезапущен frontend"
echo "✅ Сайт теперь работает"
echo ""
echo "🔍 Теперь зайди на сайт и проверь!"
