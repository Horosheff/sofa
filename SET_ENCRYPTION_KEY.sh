#!/bin/bash

# 🔐 УСТАНОВКА ПОСТОЯННОГО КЛЮЧА ШИФРОВАНИЯ
echo "🔐 УСТАНОВКА ПОСТОЯННОГО КЛЮЧА ШИФРОВАНИЯ"
echo "=========================================="

# 1. ГЕНЕРИРУЕМ ПОСТОЯННЫЙ КЛЮЧ
echo "1️⃣ Генерируем постоянный ключ шифрования..."
cd /opt/sofiya/backend
source venv/bin/activate
ENCRYPTION_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode('utf-8'))")
echo "Сгенерированный ключ: $ENCRYPTION_KEY"

# 2. ДОБАВЛЯЕМ В .ENV ФАЙЛ
echo ""
echo "2️⃣ Добавляем ключ в .env файл..."
if [ ! -f .env ]; then
    echo "Создаем .env файл..."
    touch .env
fi

# Проверяем есть ли уже ENCRYPTION_KEY
if grep -q "ENCRYPTION_KEY" .env; then
    echo "⚠️  ENCRYPTION_KEY уже существует в .env"
    echo "Текущее значение:"
    grep "ENCRYPTION_KEY" .env
    echo ""
    read -p "Заменить на новый ключ? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sed -i "s|^ENCRYPTION_KEY=.*|ENCRYPTION_KEY=$ENCRYPTION_KEY|" .env
        echo "✅ Ключ обновлен"
    else
        echo "❌ Ключ НЕ обновлен"
    fi
else
    echo "ENCRYPTION_KEY=$ENCRYPTION_KEY" >> .env
    echo "✅ Ключ добавлен в .env"
fi

# 3. ДОБАВЛЯЕМ В ECOSYSTEM.CONFIG.JS
echo ""
echo "3️⃣ Добавляем ключ в ecosystem.config.js..."
cd /opt/sofiya

# Проверяем есть ли ecosystem.config.js
if [ -f ecosystem.config.js ]; then
    # Добавляем ENCRYPTION_KEY в env секцию
    python3 << PYTHON_SCRIPT
import json
import re

with open('ecosystem.config.js', 'r') as f:
    content = f.read()

# Проверяем есть ли уже ENCRYPTION_KEY
if 'ENCRYPTION_KEY' in content:
    print("⚠️  ENCRYPTION_KEY уже есть в ecosystem.config.js")
else:
    # Ищем секцию env и добавляем ключ
    if 'env:' in content:
        # Добавляем после env: {
        content = content.replace(
            'env: {',
            f'env: {{\n        ENCRYPTION_KEY: "$ENCRYPTION_KEY",'
        )
        print("✅ ENCRYPTION_KEY добавлен в ecosystem.config.js")
    else:
        print("❌ Не найдена секция env в ecosystem.config.js")

with open('ecosystem.config.js', 'w') as f:
    f.write(content)
PYTHON_SCRIPT
else
    echo "❌ ecosystem.config.js не найден"
fi

# 4. ПЕРЕЗАПУСКАЕМ BACKEND С НОВЫМ КЛЮЧОМ
echo ""
echo "4️⃣ Перезапускаем backend с новым ключом..."
pm2 restart backend --update-env

# 5. ЖДЕМ ЗАПУСКА
echo "5️⃣ Ждем запуска..."
sleep 5

# 6. ПРОВЕРЯЕМ ЛОГИ
echo "6️⃣ Проверяем логи..."
pm2 logs backend --lines 20 --nostream | grep -A 5 "ENCRYPTION_KEY"

# 7. ПРОВЕРЯЕМ СТАТУС
echo ""
echo "7️⃣ Проверяем статус..."
pm2 status

echo ""
echo "🎯 КЛЮЧ ШИФРОВАНИЯ УСТАНОВЛЕН!"
echo "✅ ENCRYPTION_KEY: $ENCRYPTION_KEY"
echo "✅ Ключ сохранен в backend/.env"
echo "✅ Backend перезапущен"
echo ""
echo "⚠️  ВАЖНО: Сохрани этот ключ в безопасном месте!"
echo "Без него невозможно расшифровать токены в базе данных."
echo ""
echo "Теперь зайди в настройки и заново сохрани токен Telegram!"
