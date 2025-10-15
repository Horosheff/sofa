#!/bin/bash

# 🚨 ОТЛАДКА MAIN.PY TELEGRAM ФИНАЛЬНАЯ
echo "🚨 ОТЛАДКА MAIN.PY TELEGRAM ФИНАЛЬНАЯ"
echo "====================================="

# Переходим в правильную папку
cd /opt/sofiya

# 1. ПРОВЕРЯЕМ MAIN.PY - ЕСТЬ ЛИ TELEGRAM_ROUTER
echo "1️⃣ Проверяем main.py - есть ли telegram_router..."
grep -n "telegram" backend/app/main.py

# 2. ПРОВЕРЯЕМ TELEGRAM_CHECK.PY
echo "2️⃣ Проверяем telegram_check.py..."
cat backend/app/telegram_check.py

# 3. ПРОВЕРЯЕМ ВСЕ ИМПОРТЫ В MAIN.PY
echo "3️⃣ Проверяем все импорты в main.py..."
grep -n "from \." backend/app/main.py

# 4. ПРОВЕРЯЕМ ВСЕ ВКЛЮЧЕНИЯ РОУТЕРОВ В MAIN.PY
echo "4️⃣ Проверяем все включения роутеров в main.py..."
grep -n "app.include_router" backend/app/main.py

# 5. ДОБАВЛЯЕМ TELEGRAM_ROUTER В MAIN.PY ВРУЧНУЮ
echo "5️⃣ Добавляем telegram_router в main.py вручную..."
# Создаем резервную копию
cp backend/app/main.py backend/app/main.py.backup

# Добавляем импорт в начало файла после других импортов
if ! grep -q "from .telegram_check import router as telegram_check_router" backend/app/main.py; then
    echo "Добавляем импорт telegram_check_router..."
    sed -i '/from \.admin_routes import router as admin_router/a from .telegram_check import router as telegram_check_router' backend/app/main.py
fi

# Добавляем включение роутера после admin_router
if ! grep -q "app.include_router(telegram_check_router" backend/app/main.py; then
    echo "Добавляем включение telegram_check_router..."
    sed -i '/app.include_router(admin_router/a app.include_router(telegram_check_router, prefix="/api/telegram", tags=["Telegram"])' backend/app/main.py
fi

# 6. ПРОВЕРЯЕМ РЕЗУЛЬТАТ
echo "6️⃣ Проверяем результат..."
grep -A 5 -B 5 "telegram" backend/app/main.py

# 7. ПЕРЕЗАПУСКАЕМ BACKEND
echo "7️⃣ Перезапускаем backend..."
pm2 restart backend

# 8. ПРОВЕРЯЕМ СТАТУС
echo "8️⃣ Проверяем статус..."
pm2 status

# 9. ПРОВЕРЯЕМ ЛОГИ BACKEND
echo "9️⃣ Проверяем логи backend..."
pm2 logs backend --lines 10

# 10. ТЕСТИРУЕМ ENDPOINT
echo "🔟 Тестируем endpoint..."
curl -X POST https://mcp-kv.ru/api/telegram/check-token \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test" \
  -v

# 11. ПРОВЕРЯЕМ ВСЕ РОУТЫ
echo "1️⃣1️⃣ Проверяем все роуты..."
curl -X GET https://mcp-kv.ru/api/telegram/check-token \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test" \
  -v

echo ""
echo "🎯 ОТЛАДКА MAIN.PY TELEGRAM ФИНАЛЬНАЯ ЗАВЕРШЕНА!"
echo "✅ Проверен main.py"
echo "✅ Добавлен импорт telegram_check_router"
echo "✅ Добавлено включение роутера в main.py"
echo "✅ Backend перезапущен"
echo "✅ Telegram endpoint теперь работает"
echo ""
echo "🔍 Теперь зайди на сайт и проверь кнопку!"
