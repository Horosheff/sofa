#!/bin/bash

# 🔍 ДИАГНОСТИКА /mcp/tools OUTPUT
echo "🔍 ДИАГНОСТИКА /mcp/tools OUTPUT"
echo "================================"

# 1. ПРОВЕРЯЕМ ЧТО ВОЗВРАЩАЕТ /mcp/tools
echo "1️⃣ Проверяем что возвращает /mcp/tools..."
curl -s https://mcp-kv.ru/mcp/tools | python3 -m json.tool | head -50

echo ""
echo "================================"
echo ""

# 2. ПРОВЕРЯЕМ ОПРЕДЕЛЕНИЕ GET_AVAILABLE_TOOLS В MAIN.PY
echo "2️⃣ Проверяем определение get_available_tools в main.py..."
cd /opt/sofiya/backend/app
grep -A 30 "@app.get(\"/mcp/tools\")" main.py

echo ""
echo "================================"
echo ""

# 3. ПРОВЕРЯЕМ ЧТО ВОЗВРАЩАЕТ GET_ALL_MCP_TOOLS
echo "3️⃣ Проверяем структуру get_all_mcp_tools..."
grep -A 5 "def get_all_mcp_tools" ../app/mcp_handlers.py

echo ""
echo "🎯 ДИАГНОСТИКА ЗАВЕРШЕНА!"
echo ""
echo "Если /mcp/tools возвращает массив объектов вместо словаря с категориями,"
echo "то нужно исправить endpoint в main.py"
