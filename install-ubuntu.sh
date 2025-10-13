#!/bin/bash

# WordPress MCP Platform - Ubuntu Installation Script
# Установка без Docker на Ubuntu 20.04+

echo "🚀 Установка WordPress MCP Platform на Ubuntu..."

# Обновление системы
echo "📦 Обновляем систему..."
apt update && apt upgrade -y

# Установка Node.js 18
echo "📦 Устанавливаем Node.js 18..."
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt install -y nodejs

# Установка Python 3.11
echo "📦 Устанавливаем Python 3.11..."
apt install -y software-properties-common
add-apt-repository ppa:deadsnakes/ppa -y
apt update
apt install -y python3.11 python3.11-venv python3.11-dev

# Установка системных зависимостей
echo "📦 Устанавливаем системные зависимости..."
apt install -y nginx redis-server sqlite3 build-essential

# Создание пользователя для приложения
echo "👤 Создаем пользователя sofiya..."
useradd -m -s /bin/bash sofiya
usermod -aG sudo sofiya

# Создание директорий
echo "📁 Создаем директории..."
mkdir -p /opt/sofiya/{frontend,backend}
chown -R sofiya:sofiya /opt/sofiya

# Копирование файлов
echo "📋 Копируем файлы..."
cp -r frontend/* /opt/sofiya/frontend/
cp -r backend/* /opt/sofiya/backend/

# Установка зависимостей frontend
echo "📦 Устанавливаем зависимости frontend..."
cd /opt/sofiya/frontend
sudo -u sofiya npm install
sudo -u sofiya npm run build

# Установка зависимостей backend
echo "📦 Устанавливаем зависимости backend..."
cd /opt/sofiya/backend
sudo -u sofiya python3.11 -m venv venv
sudo -u sofiya ./venv/bin/pip install -r requirements.txt

# Создание systemd сервисов
echo "⚙️ Создаем systemd сервисы..."

# Backend service
cat > /etc/systemd/system/sofiya-backend.service << 'EOF'
[Unit]
Description=WordPress MCP Platform Backend
After=network.target

[Service]
Type=simple
User=sofiya
WorkingDirectory=/opt/sofiya/backend
Environment=PATH=/opt/sofiya/backend/venv/bin
ExecStart=/opt/sofiya/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Frontend service
cat > /etc/systemd/system/sofiya-frontend.service << 'EOF'
[Unit]
Description=WordPress MCP Platform Frontend
After=network.target

[Service]
Type=simple
User=sofiya
WorkingDirectory=/opt/sofiya/frontend
Environment=NODE_ENV=production
ExecStart=/usr/bin/npm start
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Nginx конфигурация
echo "🌐 Настраиваем Nginx..."
cat > /etc/nginx/sites-available/sofiya << 'EOF'
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Активация сайта
ln -sf /etc/nginx/sites-available/sofiya /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Инициализация базы данных
echo "🗄️ Инициализируем базу данных..."
cd /opt/sofiya/backend
sudo -u sofiya ./venv/bin/python init_db.py

# Запуск сервисов
echo "🚀 Запускаем сервисы..."
systemctl daemon-reload
systemctl enable sofiya-backend sofiya-frontend redis-server nginx
systemctl start redis-server
systemctl start sofiya-backend
systemctl start sofiya-frontend
systemctl restart nginx

# Проверка статуса
echo "📊 Проверяем статус сервисов..."
systemctl status sofiya-backend --no-pager
systemctl status sofiya-frontend --no-pager

echo "✅ Установка завершена!"
echo "🌐 Frontend: http://$(curl -s ifconfig.me):3000"
echo "🔧 Backend API: http://$(curl -s ifconfig.me):8000"
echo "📚 API Docs: http://$(curl -s ifconfig.me):8000/docs"

echo "📋 Управление сервисами:"
echo "  systemctl start sofiya-backend"
echo "  systemctl start sofiya-frontend"
echo "  systemctl stop sofiya-backend"
echo "  systemctl stop sofiya-frontend"
echo "  systemctl restart sofiya-backend"
echo "  systemctl restart sofiya-frontend"
