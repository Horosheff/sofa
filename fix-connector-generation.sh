#!/bin/bash

echo "🔧 ИСПРАВЛЯЕМ ГЕНЕРАЦИЮ ID КОННЕКТОРА..."

# 1. Скачиваем обновленный main.py
echo "📥 Скачиваем обновленный main.py..."
wget -q https://raw.githubusercontent.com/Horosheff/sofiya/main/backend/app/main.py -O /tmp/main.py

# 2. Заменяем файл
echo "📋 Заменяем main.py..."
cp /tmp/main.py /opt/sofiya/backend/app/main.py

# 3. Исправляем URL
echo "🔧 Исправляем URL..."
sed -i "s/mcp-kov4eg.com/mcp-kv.ru/g" /opt/sofiya/backend/app/main.py

# 4. Перезапускаем backend
echo "🔄 Перезапускаем backend..."
systemctl restart sofiya-backend

# 5. Проверяем статус
echo "✅ Проверяем статус..."
systemctl status sofiya-backend --no-pager -l

echo "🎉 ID КОННЕКТОРА ТЕПЕРЬ ГЕНЕРИРУЕТСЯ АВТОМАТИЧЕСКИ!"
