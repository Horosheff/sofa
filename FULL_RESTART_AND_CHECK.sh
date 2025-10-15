#!/bin/bash

# 🔄 ПОЛНЫЙ ПЕРЕЗАПУСК И ПРОВЕРКА
echo "🔄 ПОЛНЫЙ ПЕРЕЗАПУСК И ПРОВЕРКА"
echo "==============================="

cd /opt/sofiya

# 1. ПРОВЕРЯЕМ ЧТО ВОЗВРАЩАЕТ /mcp/tools ДО ПЕРЕЗАПУСКА
echo "1️⃣ Проверяем что возвращает /mcp/tools ДО перезапуска..."
curl -s https://mcp-kv.ru/mcp/tools > /tmp/mcp_tools_before.json
echo "Первые 100 символов:"
head -c 100 /tmp/mcp_tools_before.json
echo ""
echo ""

# 2. ПРОВЕРЯЕМ КОД ENDPOINT В MAIN.PY
echo "2️⃣ Проверяем код endpoint в main.py..."
grep -A 25 '@app.get("/mcp/tools")' backend/app/main.py
echo ""

# 3. ОСТАНАВЛИВАЕМ ВСЁ
echo "3️⃣ Останавливаем всё..."
pm2 stop all

# 4. ОЧИЩАЕМ КЭШИ
echo "4️⃣ Очищаем кэши..."
cd frontend
rm -rf .next/cache/
cd ..

# 5. ЗАПУСКАЕМ ВСЁ ЗАНОВО
echo "5️⃣ Запускаем всё заново..."
pm2 start all

# 6. ЖДЕМ ЗАПУСКА
echo "6️⃣ Ждем запуска..."
sleep 5

# 7. ПРОВЕРЯЕМ СТАТУС
echo "7️⃣ Проверяем статус..."
pm2 status

# 8. ПРОВЕРЯЕМ ЧТО ВОЗВРАЩАЕТ /mcp/tools ПОСЛЕ ПЕРЕЗАПУСКА
echo "8️⃣ Проверяем что возвращает /mcp/tools ПОСЛЕ перезапуска..."
curl -s https://mcp-kv.ru/mcp/tools > /tmp/mcp_tools_after.json
echo "Первые 100 символов:"
head -c 100 /tmp/mcp_tools_after.json
echo ""
echo ""

# 9. ПРОВЕРЯЕМ ЛОГИ BACKEND
echo "9️⃣ Проверяем логи backend..."
pm2 logs backend --lines 10 --nostream

# 10. ПРОВЕРЯЕМ ЛОГИ FRONTEND
echo "🔟 Проверяем логи frontend..."
pm2 logs frontend --lines 10 --nostream

echo ""
echo "🎯 ПОЛНЫЙ ПЕРЕЗАПУСК ЗАВЕРШЕН!"
echo ""
echo "Теперь проверь сайт в браузере!"
echo ""
echo "Если ошибка осталась, проверь файл /tmp/mcp_tools_after.json"
echo "Он должен содержать объект вида:"
echo '{"WordPress": [...], "Wordstat": [...], "Telegram": [...]}'
echo ""
echo "А НЕ массив объектов вида:"
echo '[{"name": "wordpress_get_posts", ...}, ...]'
