#!/bin/bash

echo "🔄 ПЕРЕЗАПУСКАЕМ БЕКЕНД НА СЕРВЕРЕ..."

# 1. Останавливаем backend
echo "⏹️ Останавливаем backend..."
systemctl stop sofiya-backend

# 2. Ждем 2 секунды
echo "⏳ Ждем 2 секунды..."
sleep 2

# 3. Запускаем backend
echo "▶️ Запускаем backend..."
systemctl start sofiya-backend

# 4. Ждем 3 секунды
echo "⏳ Ждем 3 секунды..."
sleep 3

# 5. Проверяем статус
echo "✅ Проверяем статус backend..."
systemctl status sofiya-backend --no-pager -l

# 6. Проверяем логи
echo "📋 Последние логи backend..."
journalctl -u sofiya-backend -n 10 --no-pager

echo "🎉 БЕКЕНД ПЕРЕЗАПУЩЕН!"
