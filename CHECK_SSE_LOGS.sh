#!/bin/bash
# 🔍 Проверка SSE логов для диагностики почему ChatGPT не видит Telegram

echo "🔍 ПРОВЕРКА SSE ЛОГОВ..."
echo ""

echo "1️⃣ Последние tools/list запросы:"
grep "tools/list" /root/.pm2/logs/backend-error.log | tail -10
echo ""

echo "2️⃣ Сколько инструментов отправлено в последнем tools/list:"
grep "Responding to tools/list with" /root/.pm2/logs/backend-error.log | tail -5
echo ""

echo "3️⃣ Последние SSE POST запросы:"
grep "SSE POST" /root/.pm2/logs/backend-error.log | tail -20
echo ""

echo "4️⃣ Проверка, что get_all_mcp_tools возвращает 99:"
cd /opt/sofiya/backend && source venv/bin/activate && python -c "from app.mcp_handlers import get_all_mcp_tools; print(f'Total tools: {len(get_all_mcp_tools())}')"
echo ""

echo "✅ ГОТОВО!"

