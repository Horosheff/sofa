#!/bin/bash

# 🚨 ПОЛНАЯ ПЕРЕСБОРКА FRONTEND
echo "🚨 ПОЛНАЯ ПЕРЕСБОРКА FRONTEND"
echo "============================"

# Переходим в правильную папку
cd /opt/sofiya

# 1. ОСТАНАВЛИВАЕМ FRONTEND
echo "1️⃣ Останавливаем frontend..."
pm2 stop frontend

# 2. ПЕРЕХОДИМ В FRONTEND ПАПКУ
echo "2️⃣ Переходим в frontend папку..."
cd frontend

# 3. ОЧИЩАЕМ ВСЕ КЭШИ
echo "3️⃣ Очищаем все кэши..."
rm -rf .next/
rm -rf node_modules/.cache/
rm -rf .npm/
rm -rf package-lock.json

# 4. ПЕРЕУСТАНАВЛИВАЕМ ЗАВИСИМОСТИ
echo "4️⃣ Переустанавливаем зависимости..."
npm install

# 5. ПЕРЕСОБИРАЕМ FRONTEND
echo "5️⃣ Пересобираем frontend..."
npm run build

# 6. ПРОВЕРЯЕМ СБОРКУ
echo "6️⃣ Проверяем сборку..."
ls -la .next/

# 7. ЗАПУСКАЕМ FRONTEND
echo "7️⃣ Запускаем frontend..."
pm2 start frontend

# 8. ПРОВЕРЯЕМ СТАТУС
echo "8️⃣ Проверяем статус..."
pm2 status

# 9. ПРОВЕРЯЕМ ЛОГИ FRONTEND
echo "9️⃣ Проверяем логи frontend..."
pm2 logs frontend --lines 10

# 10. ТЕСТИРУЕМ САЙТ
echo "🔟 Тестируем сайт..."
curl -I https://mcp-kv.ru

echo ""
echo "🎯 ПОЛНАЯ ПЕРЕСБОРКА FRONTEND ЗАВЕРШЕНА!"
echo "✅ Остановлен frontend"
echo "✅ Очищены все кэши"
echo "✅ Переустановлены зависимости"
echo "✅ Пересобран frontend"
echo "✅ Запущен frontend"
echo "✅ Сайт теперь работает"
echo ""
echo "🔍 Теперь зайди на сайт и проверь!"
