#!/bin/bash

# 🔧 Патч для исправления формата данных в backend API
# Изменяет endpoint /mcp/tools чтобы возвращать правильный формат для frontend

echo "🔧 Исправляем формат данных в backend API..."

# Перейти в папку backend
cd /opt/sofiya/backend

# Создать резервную копию
cp app/main.py app/main.py.backup_api_format

# Найти и заменить endpoint /mcp/tools
sed -i '/@app.get("\/mcp\/tools")/,/return get_all_mcp_tools()/c\
@app.get("/mcp/tools")\
async def get_available_tools():\
    """Получить список доступных MCP инструментов"""\
    # Возвращаем формат для frontend\
    tools = get_all_mcp_tools()\
    \
    # Группируем по категориям\
    wordpress_tools = []\
    wordstat_tools = []\
    telegram_tools = []\
    \
    for tool in tools:\
        if tool["name"].startswith("wordpress_"):\
            wordpress_tools.append(tool["name"].replace("wordpress_", ""))\
        elif tool["name"].startswith("wordstat_"):\
            wordstat_tools.append(tool["name"].replace("wordstat_", ""))\
        elif tool["name"].startswith("telegram_"):\
            telegram_tools.append(tool["name"].replace("telegram_", ""))\
    \
    return {\
        "WordPress": wordpress_tools,\
        "Wordstat": wordstat_tools,\
        "Telegram": telegram_tools\
    }' app/main.py

echo "✅ Патч применен успешно!"

# Проверить изменения
echo "📋 Проверяем изменения:"
grep -A 20 -B 5 "get_available_tools" app/main.py

echo "🚀 Теперь можно перезапустить backend:"
echo "pm2 restart backend"
echo "curl -s https://mcp-kv.ru/api/mcp/tools | head -10"
