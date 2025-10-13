#!/bin/bash

# Быстрое развертывание WordPress MCP Platform на сервере
# Использует существующие образы и обновляет только код

echo "🚀 Быстрое развертывание WordPress MCP Platform..."

# Остановка сервисов
echo "⏹️ Останавливаем сервисы..."
docker-compose down

# Обновление кода (если используется git)
if [ -d ".git" ]; then
    echo "📥 Обновляем код из git..."
    git pull origin main
fi

# Пересборка только измененных сервисов
echo "🔨 Пересобираем сервисы..."
docker-compose build

# Запуск сервисов
echo "▶️ Запускаем сервисы..."
docker-compose up -d

# Ожидание запуска
echo "⏳ Ждем запуска сервисов..."
sleep 5

# Проверка статуса
echo "📊 Статус сервисов:"
docker-compose ps

# Проверка логов на ошибки
echo "📋 Проверяем логи на ошибки..."
docker-compose logs --tail=10 | grep -i error || echo "✅ Ошибок не найдено"

echo "✅ Быстрое развертывание завершено!"
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"

