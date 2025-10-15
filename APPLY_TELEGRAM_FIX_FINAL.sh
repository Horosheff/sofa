#!/bin/bash

echo "🔧 Применяем финальный фикс для Telegram токена..."

cd /opt/sofiya

# Сохранить локальные изменения
git stash

# Подтянуть изменения
git pull origin main

# Перейти в frontend
cd frontend

# Остановить frontend
pm2 stop frontend

# Удалить старый билд
rm -rf .next

# Пересобрать
echo "📦 Пересборка frontend..."
npm run build

# Запустить frontend
pm2 start frontend

# Проверить статус
pm2 status

echo ""
echo "✅ Патч применён!"
echo ""
echo "🧪 ПРОВЕРЬ В БРАУЗЕРЕ:"
echo "   1. Ctrl+Shift+R для жёсткой перезагрузки"
echo "   2. Открой DevTools (F12) → Network"
echo "   3. Введи токен: 7071960627:AAFmTfBGhdKbknz6835pQBK541jaxMKxv54"
echo "   4. Нажми 'Сохранить настройки'"
echo "   5. Посмотри в Request Payload - должно быть:"
echo "      {\"telegram_bot_token\": \"7071960627:...\"}"
echo ""

