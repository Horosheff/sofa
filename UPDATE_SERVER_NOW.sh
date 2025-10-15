#!/bin/bash
# Скрипт для обновления backend на сервере
# Запустите: bash UPDATE_SERVER_NOW.sh

echo "🔄 Обновление backend на сервере..."

# Переходим в директорию backend
cd /opt/sofiya/backend

# Получаем последние изменения
echo "📥 Получение изменений из GitHub..."
git pull origin main

# Перезапускаем backend сервис
echo "🔄 Перезапуск backend сервиса..."
sudo systemctl restart sofa-backend

# Проверяем статус
echo "✅ Проверка статуса сервиса..."
sudo systemctl status sofa-backend --no-pager

# Показываем последние 20 строк логов
echo ""
echo "📋 Последние логи:"
sudo journalctl -u sofa-backend -n 20 --no-pager

echo ""
echo "✅ Обновление завершено!"
echo "🧪 Протестируйте wordstat_get_regions_tree в ChatGPT"

