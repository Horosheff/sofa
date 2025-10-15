#!/bin/bash
# 🚨 ПРИНУДИТЕЛЬНОЕ ПРИМЕНЕНИЕ ФИНАЛЬНОГО ПАТЧА

set -e

echo "🔥 СОХРАНЯЕМ ЛОКАЛЬНЫЕ ИЗМЕНЕНИЯ..."
cd /opt/sofiya
git stash push -m "before_final_telegram_fix_$(date +%Y%m%d_%H%M%S)"

echo ""
echo "📥 ЗАГРУЖАЕМ ПАТЧ С GITHUB..."
git pull origin main

echo ""
echo "🔧 ПРИМЕНЯЕМ ФИНАЛЬНЫЙ ПАТЧ..."
chmod +x FIX_TELEGRAM_FIELD_FINAL_FINAL.sh
./FIX_TELEGRAM_FIELD_FINAL_FINAL.sh

echo ""
echo "✅ ГОТОВО!!!"
echo ""
echo "📋 ТЕПЕРЬ:"
echo "1. Открой браузер"
echo "2. Нажми Ctrl+Shift+R для Hard Refresh"
echo "3. Введи FINAL_TOKEN_12345 в поле Telegram Bot Token"
echo "4. Нажми 'Сохранить настройки'"
echo "5. Проверь: grep 'FINAL_TOKEN_12345' /root/.pm2/logs/backend-error.log"

