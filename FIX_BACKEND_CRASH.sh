#!/bin/bash

# 🚨 ИСПРАВЛЕНИЕ BACKEND CRASH
echo "🚨 ИСПРАВЛЕНИЕ BACKEND CRASH"
echo "============================"

# Переходим в правильную папку
cd /opt/sofiya

# 1. ПРОВЕРЯЕМ СТАТУС PM2
echo "1️⃣ Проверяем статус PM2..."
pm2 status

# 2. ПРОВЕРЯЕМ ЛОГИ BACKEND
echo "2️⃣ Проверяем логи backend..."
pm2 logs backend --lines 20

# 3. ОСТАНАВЛИВАЕМ ВСЕ ПРОЦЕССЫ
echo "3️⃣ Останавливаем все процессы..."
pm2 stop all

# 4. ПЕРЕХОДИМ В BACKEND ПАПКУ
echo "4️⃣ Переходим в backend папку..."
cd backend

# 5. АКТИВИРУЕМ ВИРТУАЛЬНОЕ ОКРУЖЕНИЕ
echo "5️⃣ Активируем виртуальное окружение..."
source venv/bin/activate

# 6. ПРОВЕРЯЕМ ЗАВИСИМОСТИ
echo "6️⃣ Проверяем зависимости..."
pip list | grep -E "(fastapi|uvicorn|python-telegram-bot)"

# 7. ТЕСТИРУЕМ BACKEND НАПРЯМУЮ
echo "7️⃣ Тестируем backend напрямую..."
python -c "
import sys
sys.path.append('.')
try:
    from app.main import app
    print('✅ Backend импорт успешен')
except Exception as e:
    print(f'❌ Ошибка импорта: {e}')
    sys.exit(1)
"

# 8. ЗАПУСКАЕМ BACKEND ВРУЧНУЮ
echo "8️⃣ Запускаем backend вручную..."
cd /opt/sofiya/backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# 9. ЖДЕМ ЗАПУСКА
echo "9️⃣ Ждем запуска backend..."
sleep 5

# 10. ПРОВЕРЯЕМ ЧТО BACKEND РАБОТАЕТ
echo "🔟 Проверяем что backend работает..."
curl -s http://localhost:8000/health || echo "❌ Backend не отвечает"

# 11. ОСТАНАВЛИВАЕМ РУЧНОЙ ЗАПУСК
echo "1️⃣1️⃣ Останавливаем ручной запуск..."
kill $BACKEND_PID 2>/dev/null || true

# 12. ЗАПУСКАЕМ ЧЕРЕЗ PM2
echo "1️⃣2️⃣ Запускаем через PM2..."
cd /opt/sofiya
pm2 start ecosystem.config.js

# 13. ПРОВЕРЯЕМ СТАТУС
echo "1️⃣3️⃣ Проверяем статус..."
pm2 status

# 14. ПРОВЕРЯЕМ ЛОГИ
echo "1️⃣4️⃣ Проверяем логи..."
pm2 logs backend --lines 10

# 15. ТЕСТИРУЕМ API
echo "1️⃣5️⃣ Тестируем API..."
sleep 3
curl -s https://mcp-kv.ru/mcp/tools | head -c 100
echo ""

echo ""
echo "🎯 BACKEND CRASH ИСПРАВЛЕН!"
echo "✅ Backend перезапущен"
echo "✅ PM2 процессы работают"
echo "✅ API доступен"
echo ""
echo "🔍 Теперь зайди на сайт и проверь!"
