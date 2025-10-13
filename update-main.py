#!/bin/bash

echo "🔧 ОБНОВЛЯЕМ MAIN.PY НА СЕРВЕРЕ..."

# 1. Останавливаем backend
echo "⏹️ Останавливаем backend..."
systemctl stop sofiya-backend

# 2. Скачиваем исправленный main.py
echo "📥 Скачиваем исправленный main.py..."
wget -q https://raw.githubusercontent.com/Horosheff/sofiya/main/backend/app/main.py -O /tmp/main.py

# 3. Заменяем файл
echo "📋 Заменяем main.py..."
cp /tmp/main.py /opt/sofiya/backend/app/main.py

# 4. Запускаем backend
echo "▶️ Запускаем backend..."
systemctl start sofiya-backend

# 5. Проверяем статус
echo "✅ Проверяем статус..."
systemctl status sofiya-backend --no-pager -l

echo "🎉 MAIN.PY ОБНОВЛЕН!"
