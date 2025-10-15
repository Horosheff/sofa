#!/bin/bash

echo "🧹 Очищаем старый незашифрованный токен из БД..."

cd /opt/sofiya/backend

# Очистить токен для user_id=1
sqlite3 app.db "UPDATE user_settings SET telegram_bot_token = NULL WHERE user_id = 1;"

echo "✅ Токен очищен!"

# Проверить
echo ""
echo "📊 Проверка БД:"
sqlite3 app.db "SELECT user_id, telegram_bot_token FROM user_settings WHERE user_id = 1;"

echo ""
echo "✅ Теперь зайди на https://mcp-kv.ru/dashboard"
echo "   → Перейди в Настройки"
echo "   → Введи токен бота ЗАНОВО"
echo "   → Нажми 'Сохранить настройки'"
echo "   → Проверь токен через кнопку 'Проверить токен бота'"
echo ""
echo "🔐 Токен будет автоматически зашифрован при сохранении!"

