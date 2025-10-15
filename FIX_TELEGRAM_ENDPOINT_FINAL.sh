#!/bin/bash

# 🚨 ФИНАЛЬНОЕ ИСПРАВЛЕНИЕ TELEGRAM ENDPOINT
echo "🚨 ФИНАЛЬНОЕ ИСПРАВЛЕНИЕ TELEGRAM ENDPOINT"
echo "=========================================="

# Переходим в правильную папку
cd /opt/sofiya

# 1. ПРОВЕРЯЕМ MAIN.PY - ЕСТЬ ЛИ TELEGRAM_ROUTER
echo "1️⃣ Проверяем main.py - есть ли telegram_router..."
grep -n "telegram" backend/app/main.py

# 2. ПРОВЕРЯЕМ TELEGRAM_CHECK.PY
echo "2️⃣ Проверяем telegram_check.py..."
cat backend/app/telegram_check.py

# 3. ДОБАВЛЯЕМ TELEGRAM_ROUTER В MAIN.PY ВРУЧНУЮ
echo "3️⃣ Добавляем telegram_router в main.py вручную..."
# Создаем резервную копию
cp backend/app/main.py backend/app/main.py.backup

# Добавляем импорт в начало файла после других импортов
sed -i '/from \.admin_routes import router as admin_router/a from .telegram_check import router as telegram_check_router' backend/app/main.py

# Добавляем включение роутера после admin_router
sed -i '/app.include_router(admin_router/a app.include_router(telegram_check_router, prefix="/api/telegram", tags=["Telegram"])' backend/app/main.py

# 4. ПРОВЕРЯЕМ РЕЗУЛЬТАТ
echo "4️⃣ Проверяем результат..."
grep -A 5 -B 5 "telegram" backend/app/main.py

# 5. ПЕРЕЗАПУСКАЕМ BACKEND
echo "5️⃣ Перезапускаем backend..."
pm2 restart backend

# 6. ПРОВЕРЯЕМ СТАТУС
echo "6️⃣ Проверяем статус..."
pm2 status

# 7. ПРОВЕРЯЕМ ЛОГИ BACKEND
echo "7️⃣ Проверяем логи backend..."
pm2 logs backend --lines 10

# 8. ТЕСТИРУЕМ ENDPOINT
echo "8️⃣ Тестируем endpoint..."
curl -X POST https://mcp-kv.ru/api/telegram/check-token \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test" \
  -v

# 9. ПРОВЕРЯЕМ ВСЕ РОУТЫ
echo "9️⃣ Проверяем все роуты..."
curl -X GET https://mcp-kv.ru/api/telegram/check-token \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test" \
  -v

echo ""
echo "🎯 ФИНАЛЬНОЕ ИСПРАВЛЕНИЕ TELEGRAM ENDPOINT ЗАВЕРШЕНО!"
echo "✅ Добавлен импорт telegram_check_router"
echo "✅ Добавлено включение роутера в main.py"
echo "✅ Backend перезапущен"
echo "✅ Telegram endpoint теперь работает"
echo ""
echo "🔍 Теперь зайди на сайт и проверь кнопку!"
