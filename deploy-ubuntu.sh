#!/bin/bash

# Быстрое развертывание на Ubuntu без Docker

echo "🚀 Развертывание WordPress MCP Platform на Ubuntu..."

# Остановка сервисов
echo "⏹️ Останавливаем сервисы..."
systemctl stop sofiya-frontend sofiya-backend

# Обновление кода
echo "📥 Обновляем код..."
cd /opt/sofiya
git pull origin main

# Установка зависимостей frontend
echo "📦 Обновляем зависимости frontend..."
cd /opt/sofiya/frontend
sudo -u sofiya npm install
sudo -u sofiya npm run build

# Установка зависимостей backend
echo "📦 Обновляем зависимости backend..."
cd /opt/sofiya/backend
sudo -u sofiya ./venv/bin/pip install -r requirements.txt

# Инициализация базы данных
echo "🗄️ Инициализируем базу данных..."
sudo -u sofiya ./venv/bin/python init_db.py

# Запуск сервисов
echo "▶️ Запускаем сервисы..."
systemctl start sofiya-backend
systemctl start sofiya-frontend

# Проверка статуса
echo "📊 Проверяем статус..."
systemctl status sofiya-backend --no-pager
systemctl status sofiya-frontend --no-pager

echo "✅ Развертывание завершено!"
echo "🌐 Frontend: http://$(curl -s ifconfig.me)"
echo "🔧 Backend API: http://$(curl -s ifconfig.me):8000"
echo "📚 API Docs: http://$(curl -s ifconfig.me):8000/docs"
