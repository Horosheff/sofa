#!/bin/bash

echo "🔧 ИСПРАВЛЕНИЕ decrypt_token функции..."

# Перейти в папку проекта
cd /opt/sofiya

# Активировать виртуальное окружение
source backend/venv/bin/activate

# Установить cryptography если не установлен
pip install cryptography

# Проверить что FERNET_KEY установлен
if [ -z "$FERNET_KEY" ]; then
    echo "⚠️  FERNET_KEY не установлен, генерируем новый..."
    FERNET_KEY=$(python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
    echo "FERNET_KEY=$FERNET_KEY" >> backend/.env
    echo "export FERNET_KEY=$FERNET_KEY" >> ~/.bashrc
    export FERNET_KEY=$FERNET_KEY
    echo "✅ FERNET_KEY установлен: $FERNET_KEY"
else
    echo "✅ FERNET_KEY уже установлен"
fi

# Перезапустить backend
echo "🔄 Перезапуск backend..."
pm2 restart backend

# Проверить статус
echo "📊 Статус PM2:"
pm2 status

# Проверить логи backend
echo "📋 Последние логи backend:"
pm2 logs backend --lines 10 --err

echo "✅ Исправление завершено!"