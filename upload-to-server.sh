#!/bin/bash

# Скрипт для передачи обновленных файлов на сервер
# Использование: ./upload-to-server.sh user@server-ip

if [ $# -eq 0 ]; then
    echo "❌ Укажите адрес сервера: ./upload-to-server.sh user@server-ip"
    exit 1
fi

SERVER=$1
REMOTE_DIR="/root/sofiya"

echo "🚀 Передача файлов на сервер $SERVER..."

# Создание архива с обновленными файлами
echo "📦 Создаем архив..."
tar -czf sofiya-update.tar.gz \
    --exclude=node_modules \
    --exclude=.git \
    --exclude=*.db \
    --exclude=.next \
    --exclude=__pycache__ \
    --exclude=*.pyc \
    frontend/ \
    backend/ \
    docker-compose.yml \
    deploy.sh \
    quick-deploy.sh \
    README.md \
    .gitignore

# Передача архива на сервер
echo "📤 Передаем архив на сервер..."
scp sofiya-update.tar.gz $SERVER:/tmp/

# Распаковка и обновление на сервере
echo "📥 Распаковываем и обновляем на сервере..."
ssh $SERVER << 'EOF'
cd /root
if [ -d "sofiya" ]; then
    echo "📁 Создаем резервную копию..."
    cp -r sofiya sofiya-backup-$(date +%Y%m%d-%H%M%S)
fi

echo "📦 Распаковываем обновления..."
tar -xzf /tmp/sofiya-update.tar.gz

echo "🔧 Устанавливаем права доступа..."
chmod +x sofiya/deploy.sh
chmod +x sofiya/quick-deploy.sh

echo "🧹 Очищаем временные файлы..."
rm /tmp/sofiya-update.tar.gz

echo "✅ Файлы обновлены на сервере!"
EOF

# Очистка локального архива
echo "🧹 Очищаем локальный архив..."
rm sofiya-update.tar.gz

echo "🎉 Передача завершена!"
echo "📋 Для развертывания на сервере выполните:"
echo "   ssh $SERVER 'cd /root/sofiya && ./deploy.sh'"

