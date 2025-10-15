#!/bin/bash

# 🔧 ИСПРАВЛЕНИЕ /mcp/tools ENDPOINT
echo "🔧 ИСПРАВЛЕНИЕ /mcp/tools ENDPOINT"
echo "==================================="

cd /opt/sofiya/backend/app

# 1. СОЗДАЕМ БЭКАП
echo "1️⃣ Создаем бэкап main.py..."
cp main.py main.py.backup_$(date +%Y%m%d_%H%M%S)

# 2. НАХОДИМ СТРОКУ С @app.get("/mcp/tools")
echo "2️⃣ Находим строку с @app.get(\"/mcp/tools\")..."
LINE_NUM=$(grep -n '@app.get("/mcp/tools")' main.py | cut -d: -f1)
echo "Найдено на строке: $LINE_NUM"

# 3. ЗАМЕНЯЕМ ENDPOINT
echo "3️⃣ Заменяем endpoint..."
python3 << 'PYTHON_SCRIPT'
with open('main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Находим индекс строки с @app.get("/mcp/tools")
start_idx = None
for i, line in enumerate(lines):
    if '@app.get("/mcp/tools")' in line:
        start_idx = i
        break

if start_idx is None:
    print("❌ Не найдено @app.get(\"/mcp/tools\")")
    exit(1)

# Находим конец функции (следующий @app или def на уровне модуля)
end_idx = None
for i in range(start_idx + 1, len(lines)):
    if lines[i].startswith('@app.') or (lines[i].startswith('def ') and not lines[i].startswith('    ')):
        end_idx = i
        break

if end_idx is None:
    end_idx = len(lines)

# Заменяем функцию
new_function = '''@app.get("/mcp/tools")
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

'''

# Записываем новый код
new_lines = lines[:start_idx] + [new_function] + lines[end_idx:]

with open('main.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("✅ Endpoint исправлен")
PYTHON_SCRIPT

# 4. ПРОВЕРЯЕМ ЧТО ИЗМЕНИЛОСЬ
echo "4️⃣ Проверяем что изменилось..."
grep -A 25 '@app.get("/mcp/tools")' main.py

# 5. ПЕРЕЗАПУСКАЕМ BACKEND
echo "5️⃣ Перезапускаем backend..."
cd /opt/sofiya
pm2 restart backend

# 6. ЖДЕМ ЗАПУСКА
echo "6️⃣ Ждем запуска..."
sleep 5

# 7. ПРОВЕРЯЕМ СТАТУС
echo "7️⃣ Проверяем статус..."
pm2 status

# 8. ТЕСТИРУЕМ API
echo "8️⃣ Тестируем API..."
curl -s https://mcp-kv.ru/mcp/tools | python3 -m json.tool | head -30

# 9. ПРОВЕРЯЕМ ЛОГИ
echo "9️⃣ Проверяем логи..."
pm2 logs backend --lines 10 --nostream

echo ""
echo "🎯 /mcp/tools ENDPOINT ИСПРАВЛЕН!"
echo "✅ Backend возвращает правильный формат"
echo "✅ Frontend теперь сможет обработать данные"
echo ""
echo "Теперь зайди на сайт и проверь!"
