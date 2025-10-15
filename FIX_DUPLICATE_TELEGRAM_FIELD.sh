#!/bin/bash

# 🔧 Автоматический патч для исправления дублирования has_telegram_bot
# Полностью пересоздает интерфейс UserSettings

echo "🔧 Исправляем дублирование has_telegram_bot в ToolsPanel.tsx..."

# Перейти в папку frontend
cd /opt/sofiya/frontend

# Создать резервную копию
cp components/ToolsPanel.tsx components/ToolsPanel.tsx.backup_duplicate_fix

# Найти и заменить весь интерфейс UserSettings
sed -i '/interface UserSettings {/,/}/c\
interface UserSettings {\
  has_wordpress_credentials: boolean\
  has_wordstat_credentials: boolean\
  has_telegram_bot: boolean\
}' components/ToolsPanel.tsx

echo "✅ Патч применен успешно!"

# Проверить результат
echo "📋 Проверяем результат:"
grep -A 5 -B 5 "has_telegram_bot" components/ToolsPanel.tsx

echo "🚀 Теперь можно пересобрать frontend:"
echo "rm -rf .next"
echo "npm run build"
echo "pm2 restart frontend"
