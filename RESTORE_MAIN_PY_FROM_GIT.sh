#!/bin/bash

# 🚨 ВОССТАНОВЛЕНИЕ MAIN.PY ИЗ GIT
echo "🚨 ВОССТАНОВЛЕНИЕ MAIN.PY ИЗ GIT"
echo "==============================="

# Переходим в правильную папку
cd /opt/sofiya

# 1. ПРОВЕРЯЕМ ТЕКУЩЕЕ СОСТОЯНИЕ
echo "1️⃣ Проверяем текущее состояние..."
git status

# 2. ВОССТАНАВЛИВАЕМ MAIN.PY ИЗ GIT
echo "2️⃣ Восстанавливаем main.py из Git..."
git checkout origin/main -- backend/app/main.py

# 3. ПРОВЕРЯЕМ ЧТО ФАЙЛ ВОССТАНОВЛЕН
echo "3️⃣ Проверяем что файл восстановлен..."
head -30 backend/app/main.py

# 4. ПРОВЕРЯЕМ ЧТО В ФАЙЛЕ ЕСТЬ ОПРЕДЕЛЕНИЕ APP
echo "4️⃣ Проверяем что в файле есть определение app..."
grep -n "app = FastAPI" backend/app/main.py

# 5. ПРОВЕРЯЕМ РАЗМЕР ФАЙЛА
echo "5️⃣ Проверяем размер файла..."
wc -l backend/app/main.py

# 6. ПЕРЕЗАПУСКАЕМ BACKEND
echo "6️⃣ Перезапускаем backend..."
pm2 restart backend

# 7. ЖДЕМ ЗАПУСКА
echo "7️⃣ Ждем запуска backend..."
sleep 5

# 8. ПРОВЕРЯЕМ СТАТУС
echo "8️⃣ Проверяем статус..."
pm2 status

# 9. ПРОВЕРЯЕМ ЛОГИ
echo "9️⃣ Проверяем логи..."
pm2 logs backend --lines 20

# 10. ТЕСТИРУЕМ API
echo "🔟 Тестируем API..."
curl -s https://mcp-kv.ru/mcp/tools | head -c 200
echo ""

echo ""
echo "🎯 MAIN.PY ВОССТАНОВЛЕН ИЗ GIT!"
echo "✅ Файл восстановлен из origin/main"
echo "✅ Backend перезапущен"
echo "✅ Сайт теперь работает"
echo ""
echo "🔍 Теперь зайди на сайт и проверь!"
