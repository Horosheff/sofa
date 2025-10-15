#!/bin/bash

# 🔧 Финальный патч для исправления TypeScript ошибки
# Исправляет инициализацию settings в ToolsPanel.tsx

echo "🔧 Исправляем TypeScript ошибку в ToolsPanel.tsx..."

# Перейти в папку frontend
cd /opt/sofiya/frontend

# Создать резервную копию
cp components/ToolsPanel.tsx components/ToolsPanel.tsx.backup_final

# Исправить инициализацию settings - добавить has_telegram_bot: false
sed -i '/has_wordstat_credentials: false,$/a\    has_telegram_bot: false,' components/ToolsPanel.tsx

echo "✅ Патч применен успешно!"

# Проверить изменения
echo "📋 Проверяем изменения:"
grep -A 5 -B 5 "has_telegram_bot" components/ToolsPanel.tsx

echo "🚀 Теперь можно пересобрать frontend:"
echo "npm run build"
echo "pm2 restart frontend"
