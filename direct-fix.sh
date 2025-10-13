#!/bin/bash

echo "🔧 ПРЯМОЕ ИСПРАВЛЕНИЕ URL НА СЕРВЕРЕ..."

# 1. Исправляем auth.py - меняем kov4eg на kv
echo "📝 Исправляем auth.py..."
sed -i "s/mcp-kov4eg.com/mcp-kv.ru/g" /opt/sofiya/backend/app/auth.py

# 2. Исправляем main.py - меняем kov4eg на kv  
echo "📝 Исправляем main.py..."
sed -i "s/mcp-kov4eg.com/mcp-kv.ru/g" /opt/sofiya/backend/app/main.py

# 3. Перезапускаем backend
echo "🔄 Перезапускаем backend..."
systemctl restart sofiya-backend

# 4. Проверяем что изменилось
echo "✅ Проверяем изменения..."
echo "auth.py:"
grep "mcp-kv.ru" /opt/sofiya/backend/app/auth.py
echo "main.py:"
grep "mcp-kv.ru" /opt/sofiya/backend/app/main.py

echo "🎉 URL ИСПРАВЛЕН НА mcp-kv.ru!"
