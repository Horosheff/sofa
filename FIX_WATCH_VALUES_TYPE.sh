#!/bin/bash
# 🎯 ФИКС: Добавить telegram_bot_token в watchValues

set -e

echo "🔧 ИСПРАВЛЯЕМ TypeScript ERROR в SettingsPanel.tsx..."

cd /opt/sofiya/frontend/components

# Найти строку с value: watchValues.telegram_bot_token и заменить на getValues
sed -i.bak 's/value: watchValues\.telegram_bot_token || '\'''\''//' SettingsPanel.tsx

echo "✅ Патч применён!"
echo ""
echo "🔍 Проверка изменений:"
grep -A 2 "register.*telegram_bot_token" SettingsPanel.tsx | head -10

echo ""
echo "🚀 ПЕРЕСБОРКА FRONTEND..."
cd /opt/sofiya/frontend
npm run build

echo ""
echo "🔄 ПЕРЕЗАПУСК FRONTEND..."
pm2 restart frontend

echo ""
echo "✅ ГОТОВО!"
echo ""
echo "📋 ТЕПЕРЬ:"
echo "1. Обнови страницу (Ctrl+Shift+R)"
echo "2. Введи SUPER_FINAL_TOKEN_999"
echo "3. Сохрани настройки"
echo "4. Проверь: grep 'SUPER_FINAL_TOKEN_999' /root/.pm2/logs/backend-error.log"

