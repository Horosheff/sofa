#!/bin/bash

echo "🔧 ИСПРАВЛЯЕМ FRONTEND - УБИРАЕМ /api/ ПРЕФИКС..."

# 1. Скачиваем обновленный SettingsPanel.tsx
echo "📥 Скачиваем обновленный SettingsPanel.tsx..."
wget -q https://raw.githubusercontent.com/Horosheff/sofiya/main/frontend/components/SettingsPanel.tsx -O /tmp/SettingsPanel.tsx

# 2. Заменяем файл
echo "📋 Заменяем SettingsPanel.tsx..."
cp /tmp/SettingsPanel.tsx /opt/sofiya/frontend/components/SettingsPanel.tsx

# 3. Перезапускаем frontend
echo "🔄 Перезапускаем frontend..."
systemctl restart sofiya-frontend

# 4. Проверяем статус
echo "✅ Проверяем статус frontend..."
systemctl status sofiya-frontend --no-pager -l

echo "🎉 FRONTEND ИСПРАВЛЕН - ТЕПЕРЬ БУДЕТ ЗАПРАШИВАТЬ ДАННЫЕ!"
