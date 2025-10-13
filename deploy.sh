#!/bin/bash

# Скрипт развертывания WordPress MCP Platform

echo "🚀 Начинаем развертывание WordPress MCP Platform..."

# Проверяем наличие Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен. Установите Docker и попробуйте снова."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose не установлен. Установите Docker Compose и попробуйте снова."
    exit 1
fi

# Останавливаем существующие контейнеры
echo "🛑 Останавливаем существующие контейнеры..."
docker-compose down

# Собираем образы
echo "🔨 Собираем Docker образы..."
docker-compose build --no-cache

# Запускаем сервисы
echo "🚀 Запускаем сервисы..."
docker-compose up -d

# Проверяем статус
echo "📊 Проверяем статус сервисов..."
docker-compose ps

# Ждем запуска сервисов
echo "⏳ Ждем запуска сервисов..."
sleep 10

# Проверяем доступность
echo "🔍 Проверяем доступность сервисов..."

# Проверяем backend
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend доступен на http://localhost:8000"
else
    echo "❌ Backend недоступен"
fi

# Проверяем frontend
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend доступен на http://localhost:3000"
else
    echo "❌ Frontend недоступен"
fi

echo "🎉 Развертывание завершено!"
echo ""
echo "📋 Доступные сервисы:"
echo "   🌐 Frontend: http://localhost:3000"
echo "   🔧 Backend API: http://localhost:8000"
echo "   📊 API Docs: http://localhost:8000/docs"
echo "   🔴 Redis: localhost:6379"
echo ""
echo "📝 Логи сервисов:"
echo "   docker-compose logs -f"
echo ""
echo "🛑 Остановка сервисов:"
echo "   docker-compose down"
