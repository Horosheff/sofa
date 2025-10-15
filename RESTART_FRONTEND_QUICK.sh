#!/bin/bash

# 🚀 БЫСТРЫЙ ПЕРЕЗАПУСК FRONTEND
echo "🚀 БЫСТРЫЙ ПЕРЕЗАПУСК FRONTEND"
echo "=============================="

# 1. ПРОВЕРЯЕМ ТЕКУЩИЙ СТАТУС
echo "1️⃣ Проверяем текущий статус..."
pm2 status

# 2. ОСТАНАВЛИВАЕМ FRONTEND
echo "2️⃣ Останавливаем frontend..."
pm2 stop frontend

# 3. ОЧИЩАЕМ КЭШ
echo "3️⃣ Очищаем кэш..."
cd /opt/sofiya/frontend
rm -rf .next
rm -rf node_modules/.cache

# 4. ПЕРЕСОБИРАЕМ
echo "4️⃣ Пересобираем frontend..."
npm run build

# 5. ЗАПУСКАЕМ FRONTEND
echo "5️⃣ Запускаем frontend..."
pm2 start frontend

# 6. ЖДЕМ 3 СЕКУНДЫ
echo "6️⃣ Ждем 3 секунды..."
sleep 3

# 7. ПРОВЕРЯЕМ СТАТУС
echo "7️⃣ Проверяем статус..."
pm2 status

# 8. ПРОВЕРЯЕМ ЛОГИ
echo "8️⃣ Проверяем логи frontend..."
pm2 logs frontend --lines 5

# 9. ТЕСТИРУЕМ САЙТ
echo "9️⃣ Тестируем сайт..."
curl -I https://mcp-kv.ru

echo ""
echo "🎯 FRONTEND ПЕРЕЗАПУЩЕН!"
echo "✅ Кэш очищен"
echo "✅ Frontend пересобран"
echo "✅ Сервис перезапущен"
echo ""
echo "🔍 Теперь зайди на https://mcp-kv.ru и проверь настройки!"
echo "📋 Должна появиться кнопка '🔍 Проверить бота' в секции Telegram"
