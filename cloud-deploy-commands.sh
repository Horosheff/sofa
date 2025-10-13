#!/bin/bash

# Команды для развертывания на облачном сервере
# Выполните эти команды после подключения к серверу

echo "🚀 Начинаем развертывание WordPress MCP Platform на облаке..."

# Обновляем систему
echo "📦 Обновляем систему..."
apt update && apt upgrade -y

# Устанавливаем Docker
echo "🐳 Устанавливаем Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
rm get-docker.sh

# Устанавливаем Docker Compose
echo "🔧 Устанавливаем Docker Compose..."
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Устанавливаем Git
echo "📥 Устанавливаем Git..."
apt install git -y

# Клонируем репозиторий
echo "📂 Клонируем репозиторий..."
git clone https://github.com/Horosheff/sofiya.git
cd sofiya

# Настраиваем production переменные
echo "⚙️ Настраиваем production переменные..."
cp env.production .env

# Генерируем секретный ключ
SECRET_KEY=$(openssl rand -hex 32)
sed -i "s/your-very-secure-production-secret-key-change-this-immediately/$SECRET_KEY/" .env

# Обновляем домены (замените на ваш домен)
echo "🌐 Настройте домены в .env файле:"
echo "nano .env"
echo "Измените:"
echo "- ALLOWED_ORIGINS=https://yourdomain.com"
echo "- NGINX_HOST=yourdomain.com"

# Создаем директорию для SSL
echo "🔒 Создаем директорию для SSL сертификатов..."
mkdir -p ssl

# Запускаем развертывание
echo "🚀 Запускаем развертывание..."
chmod +x deploy.sh
./deploy.sh

echo "✅ Развертывание завершено!"
echo ""
echo "📋 Следующие шаги:"
echo "1. Настройте SSL сертификаты в папке ssl/"
echo "2. Обновите домены в .env файле"
echo "3. Перезапустите сервисы: docker-compose restart"
echo ""
echo "🌐 Доступные сервисы:"
echo "- Frontend: http://your-ip:3000"
echo "- Backend: http://your-ip:8000"
echo "- API Docs: http://your-ip:8000/docs"
