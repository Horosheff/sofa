#!/bin/bash
# 🎯 ФИНАЛЬНОЕ РЕШЕНИЕ: React Hook Form не отправляет пустые поля
# Решение: добавить shouldUnregister: false и всегда включать значение

set -e

echo "🔧 ФИНАЛЬНЫЙ ПАТЧ: Принудительная отправка telegram_bot_token..."

cd /opt/sofiya/frontend/components

# Найти строку с register для telegram_bot_token и добавить правильные опции
sed -i.bak '/register.*telegram_bot_token/c\
                  {...register('\''telegram_bot_token'\'', { \
                    shouldUnregister: false, \
                    value: watchValues.telegram_bot_token || '\'''\'' \
                  })}' SettingsPanel.tsx

echo "✅ Патч применён!"
echo ""
echo "🔍 Проверка изменений:"
grep -A 3 "register.*telegram_bot_token" SettingsPanel.tsx || echo "⚠️ Паттерн не найден"

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
echo "2. Введи NEW_TOKEN_FINAL_999"
echo "3. Сохрани настройки"
echo "4. Проверь логи: grep 'NEW_TOKEN_FINAL_999' /root/.pm2/logs/backend-error.log"

