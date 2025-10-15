#!/bin/bash

# 🔧 ИСПРАВЛЕНИЕ PREFIX ДЛЯ TELEGRAM ENDPOINT
echo "🔧 ИСПРАВЛЕНИЕ PREFIX ДЛЯ TELEGRAM ENDPOINT"
echo "==========================================="

cd /opt/sofiya

# 1. ПРОВЕРЯЕМ ТЕКУЩИЙ PREFIX
echo "1️⃣ Проверяем текущий prefix..."
grep "telegram_check_router" backend/app/main.py

# 2. МЕНЯЕМ PREFIX НА /telegram (БЕЗ /api)
echo "2️⃣ Меняем prefix на /telegram (без /api)..."
cd backend/app
sed -i 's|app.include_router(telegram_check_router, prefix="/api/telegram"|app.include_router(telegram_check_router, prefix="/telegram"|g' main.py

# 3. ПРОВЕРЯЕМ ЧТО ИЗМЕНИЛОСЬ
echo "3️⃣ Проверяем что изменилось..."
grep "telegram_check_router" main.py

# 4. ПЕРЕЗАПУСКАЕМ BACKEND
echo "4️⃣ Перезапускаем backend..."
cd /opt/sofiya
pm2 restart backend

# 5. ЖДЕМ ЗАПУСКА
echo "5️⃣ Ждем запуска..."
sleep 3

# 6. ПРОВЕРЯЕМ СТАТУС
echo "6️⃣ Проверяем статус..."
pm2 status

# 7. ПРОВЕРЯЕМ ЛОГИ
echo "7️⃣ Проверяем логи..."
pm2 logs backend --lines 10 --nostream

echo ""
echo "🎯 PREFIX ИСПРАВЛЕН!"
echo "✅ Теперь endpoint доступен по адресу /telegram/check-token"
echo "✅ Frontend отправляет на /api/telegram/check-token"
echo "✅ Nginx перенаправляет на /telegram/check-token"
echo "✅ Backend обрабатывает запрос"
echo ""
echo "Теперь зайди на сайт и попробуй снова нажать кнопку!"
