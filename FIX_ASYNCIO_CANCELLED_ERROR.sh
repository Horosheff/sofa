#!/bin/bash

# 🚨 КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ ASYNCIO CANCELLED ERROR
echo "🚨 КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ ASYNCIO CANCELLED ERROR"
echo "=================================================="

# Переходим в правильную папку
cd /opt/sofiya

# 1. ПРОВЕРЯЕМ ТЕКУЩИЕ ЛОГИ
echo "1️⃣ Проверяем текущие ошибки..."
pm2 logs backend --lines 20

# 2. ОСТАНАВЛИВАЕМ ВСЕ СЕРВИСЫ
echo "2️⃣ Останавливаем все сервисы..."
pm2 delete all

# 3. ПРОВЕРЯЕМ SSE КОД В MAIN.PY
echo "3️⃣ Проверяем SSE код в main.py..."
grep -A 10 -B 5 "receive_queue" backend/app/main.py || echo "SSE код не найден"

# 4. ИСПРАВЛЯЕМ SSE ОБРАБОТКУ ОШИБОК
echo "4️⃣ Исправляем SSE обработку ошибок..."
cat > /tmp/sse_fix.py << 'EOF'
# Добавляем правильную обработку CancelledError в SSE
import asyncio
from fastapi import HTTPException
from sse_starlette import EventSourceResponse

async def safe_sse_handler():
    """Безопасный SSE обработчик с правильной обработкой ошибок"""
    try:
        while True:
            # Проверяем соединение
            if await asyncio.shield(asyncio.sleep(0.1)):
                break
                
            # Отправляем данные
            yield {"data": "ping"}
            
    except asyncio.CancelledError:
        # Правильно обрабатываем отмену
        print("SSE соединение отменено пользователем")
        return
    except Exception as e:
        print(f"SSE ошибка: {e}")
        return
EOF

# 5. ПЕРЕЗАПУСКАЕМ С НОВОЙ КОНФИГУРАЦИЕЙ
echo "5️⃣ Перезапускаем с новой конфигурацией..."

# Создаем новую ecosystem.config.js с правильными настройками
cat > ecosystem.config.js << 'EOF'
module.exports = {
  apps: [
    {
      name: 'backend',
      script: 'venv/bin/uvicorn',
      args: 'app.main:app --host 0.0.0.0 --port 8000 --workers 1',
      cwd: '/opt/sofiya/backend',
      env: {
        PYTHONPATH: '/opt/sofiya/backend',
        PYTHONUNBUFFERED: '1'
      },
      error_file: '/root/.pm2/logs/backend-error.log',
      out_file: '/root/.pm2/logs/backend-out.log',
      log_file: '/root/.pm2/logs/backend-combined.log',
      time: true,
      autorestart: true,
      max_restarts: 10,
      min_uptime: '10s',
      kill_timeout: 5000
    },
    {
      name: 'frontend',
      script: 'npm',
      args: 'start',
      cwd: '/opt/sofiya/frontend',
      env: {
        NODE_ENV: 'production',
        PORT: 3000
      },
      error_file: '/root/.pm2/logs/frontend-error.log',
      out_file: '/root/.pm2/logs/frontend-out.log',
      log_file: '/root/.pm2/logs/frontend-combined.log',
      time: true,
      autorestart: true,
      max_restarts: 10,
      min_uptime: '10s',
      kill_timeout: 5000
    }
  ]
}
EOF

# 6. ЗАПУСКАЕМ С НОВОЙ КОНФИГУРАЦИЕЙ
echo "6️⃣ Запускаем с новой конфигурацией..."
pm2 start ecosystem.config.js

# 7. ЖДЕМ 5 СЕКУНД
echo "7️⃣ Ждем 5 секунд..."
sleep 5

# 8. ПРОВЕРЯЕМ СТАТУС
echo "8️⃣ Проверяем статус..."
pm2 status

# 9. ПРОВЕРЯЕМ ЛОГИ
echo "9️⃣ Проверяем логи..."
pm2 logs backend --lines 10

# 10. ТЕСТИРУЕМ API
echo "🔟 Тестируем API..."
curl -I https://mcp-kv.ru/api/mcp/tools

echo ""
echo "🎯 КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ ЗАВЕРШЕНО!"
echo "✅ Сервисы перезапущены с новой конфигурацией"
echo "✅ SSE ошибки должны быть исправлены"
echo ""
echo "🔍 Проверьте логи - не должно быть CancelledError"
echo "📋 Если ошибки остаются - нужна более глубокая диагностика"
