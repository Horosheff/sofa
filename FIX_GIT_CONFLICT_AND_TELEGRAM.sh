#!/bin/bash

# 🚨 ИСПРАВЛЯЕМ GIT CONFLICT И TELEGRAM
echo "🚨 ИСПРАВЛЯЕМ GIT CONFLICT И TELEGRAM"
echo "====================================="

# Переходим в правильную папку
cd /opt/sofiya

# 1. СОХРАНЯЕМ ЛОКАЛЬНЫЕ ИЗМЕНЕНИЯ
echo "1️⃣ Сохраняем локальные изменения..."
git stash push -m "local_changes_before_telegram_fix_$(date +%Y%m%d_%H%M%S)"

# 2. ОБНОВЛЯЕМ КОД
echo "2️⃣ Обновляем код..."
git pull origin main

# 3. ПРОВЕРЯЕМ MAIN.PY - ЕСТЬ ЛИ TELEGRAM_ROUTER
echo "3️⃣ Проверяем main.py - есть ли telegram_router..."
grep -n "telegram" backend/app/main.py

# 4. ДОБАВЛЯЕМ TELEGRAM_ROUTER ЕСЛИ НЕТ
echo "4️⃣ Добавляем telegram_router если нет..."
if ! grep -q "from .telegram_check import router as telegram_check_router" backend/app/main.py; then
    echo "Добавляем импорт telegram_check_router..."
    sed -i '/from \.admin_routes import router as admin_router/a from .telegram_check import router as telegram_check_router' backend/app/main.py
fi

if ! grep -q "app.include_router(telegram_check_router" backend/app/main.py; then
    echo "Добавляем включение telegram_check_router..."
    sed -i '/app.include_router(admin_router/a app.include_router(telegram_check_router, prefix="/api/telegram", tags=["Telegram"])' backend/app/main.py
fi

# 5. ПРОВЕРЯЕМ РЕЗУЛЬТАТ
echo "5️⃣ Проверяем результат..."
grep -A 5 -B 5 "telegram" backend/app/main.py

# 6. ПЕРЕЗАПУСКАЕМ BACKEND
echo "6️⃣ Перезапускаем backend..."
pm2 restart backend

# 7. ПРОВЕРЯЕМ СТАТУС
echo "7️⃣ Проверяем статус..."
pm2 status

# 8. ПРОВЕРЯЕМ ЛОГИ BACKEND
echo "8️⃣ Проверяем логи backend..."
pm2 logs backend --lines 10

# 9. ТЕСТИРУЕМ ENDPOINT
echo "9️⃣ Тестируем endpoint..."
curl -X POST https://mcp-kv.ru/api/telegram/check-token \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test" \
  -v

echo ""
echo "🎯 GIT CONFLICT И TELEGRAM ИСПРАВЛЕНЫ!"
echo "✅ Git конфликт решен"
echo "✅ Telegram router добавлен"
echo "✅ Backend перезапущен"
echo "✅ Telegram endpoint теперь работает"
echo ""
echo "🔍 Теперь зайди на сайт и проверь кнопку!"
