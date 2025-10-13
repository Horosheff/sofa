#!/bin/bash

echo "🔧 ПЕРЕСБИРАЕМ FRONTEND НА СЕРВЕРЕ..."

# 1. Останавливаем frontend
echo "⏹️ Останавливаем frontend..."
systemctl stop sofiya-frontend

# 2. Скачиваем обновленный SettingsPanel.tsx
echo "📥 Скачиваем обновленный SettingsPanel.tsx..."
wget -q https://raw.githubusercontent.com/Horosheff/sofiya/main/frontend/components/SettingsPanel.tsx -O /tmp/SettingsPanel.tsx

# 3. Заменяем файл
echo "📋 Заменяем SettingsPanel.tsx..."
cp /tmp/SettingsPanel.tsx /opt/sofiya/frontend/components/SettingsPanel.tsx

# 4. Переходим в директорию frontend
cd /opt/sofiya/frontend

# 5. Очищаем кэш Next.js
echo "🧹 Очищаем кэш Next.js..."
rm -rf .next
rm -rf node_modules/.cache

# 6. Пересобираем frontend
echo "🔨 Пересобираем frontend..."
npm run build

# 7. Запускаем frontend
echo "▶️ Запускаем frontend..."
systemctl start sofiya-frontend

# 8. Проверяем статус
echo "✅ Проверяем статус..."
systemctl status sofiya-frontend --no-pager -l

echo "🎉 FRONTEND ПЕРЕСОБРАН И ЗАПУЩЕН!"
