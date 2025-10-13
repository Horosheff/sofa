#!/bin/bash

# WordPress MCP Platform - Deployment Script
# Обновляет и перезапускает все сервисы

echo "🚀 Начинаем развертывание WordPress MCP Platform..."

# Остановка существующих контейнеров
echo "⏹️ Останавливаем существующие контейнеры..."
docker-compose down

# Очистка старых образов
echo "🧹 Очищаем старые образы..."
docker system prune -f

# Сборка новых образов
echo "🔨 Собираем новые образы..."
docker-compose build --no-cache

# Запуск сервисов
echo "▶️ Запускаем сервисы..."
docker-compose up -d

# Ожидание запуска
echo "⏳ Ждем запуска сервисов..."
sleep 10

# Проверка статуса
echo "📊 Проверяем статус сервисов..."
docker-compose ps

# Проверка логов
echo "📋 Проверяем логи..."
docker-compose logs --tail=20

# Инициализация базы данных
echo "🗄️ Инициализируем базу данных..."
docker-compose exec backend python init_db.py

echo "✅ Развертывание завершено!"
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"