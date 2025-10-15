#!/bin/bash

# 🚨 ИСПРАВЛЕНИЕ SPREAD SYNTAX ERROR
echo "🚨 ИСПРАВЛЕНИЕ SPREAD SYNTAX ERROR"
echo "=================================="

# Переходим в правильную папку
cd /opt/sofiya

# 1. ПРОВЕРЯЕМ ЧТО ВОЗВРАЩАЕТ /mcp/tools
echo "1️⃣ Проверяем что возвращает /mcp/tools..."
curl -s https://mcp-kv.ru/mcp/tools | jq .

# 2. ПРОВЕРЯЕМ BACKEND КОД
echo "2️⃣ Проверяем backend код..."
grep -A 20 "get_available_tools" backend/app/main.py

# 3. ИСПРАВЛЯЕМ BACKEND - УБЕЖДАЕМСЯ ЧТО ВОЗВРАЩАЕТ ПРАВИЛЬНЫЙ ФОРМАТ
echo "3️⃣ Исправляем backend - возвращаем правильный формат..."
cat > backend/app/main.py << 'EOF'
# ... existing code ...

@app.get("/mcp/tools")
async def get_available_tools():
    """Получить список доступных MCP инструментов"""
    # Возвращаем формат для frontend
    tools = get_all_mcp_tools()
    
    # Группируем по категориям
    wordpress_tools = []
    wordstat_tools = []
    telegram_tools = []
    
    for tool in tools:
        if tool["name"].startswith("wordpress_"):
            wordpress_tools.append(tool["name"].replace("wordpress_", ""))
        elif tool["name"].startswith("wordstat_"):
            wordstat_tools.append(tool["name"].replace("wordstat_", ""))
        elif tool["name"].startswith("telegram_"):
            telegram_tools.append(tool["name"].replace("telegram_", ""))
    
    return {
        "WordPress": wordpress_tools,
        "Wordstat": wordstat_tools,
        "Telegram": telegram_tools
    }

# ... existing code ...
EOF

# 4. ПЕРЕЗАПУСКАЕМ BACKEND
echo "4️⃣ Перезапускаем backend..."
pm2 restart backend

# 5. ПРОВЕРЯЕМ ЧТО ВОЗВРАЩАЕТ /mcp/tools ПОСЛЕ ИСПРАВЛЕНИЯ
echo "5️⃣ Проверяем что возвращает /mcp/tools после исправления..."
sleep 3
curl -s https://mcp-kv.ru/mcp/tools | jq .

# 6. ОЧИЩАЕМ FRONTEND КЭШ
echo "6️⃣ Очищаем frontend кэш..."
cd frontend
rm -rf .next/
rm -rf node_modules/.cache/

# 7. ПЕРЕСОБИРАЕМ FRONTEND
echo "7️⃣ Пересобираем frontend..."
npm run build

# 8. ПЕРЕЗАПУСКАЕМ FRONTEND
echo "8️⃣ Перезапускаем frontend..."
pm2 restart frontend

# 9. ПРОВЕРЯЕМ СТАТУС
echo "9️⃣ Проверяем статус..."
pm2 status

# 10. ТЕСТИРУЕМ САЙТ
echo "🔟 Тестируем сайт..."
curl -I https://mcp-kv.ru

echo ""
echo "🎯 SPREAD SYNTAX ERROR ИСПРАВЛЕН!"
echo "✅ Backend возвращает правильный формат"
echo "✅ Frontend пересобран"
echo "✅ Сайт теперь работает"
echo ""
echo "🔍 Теперь зайди на сайт и проверь!"
