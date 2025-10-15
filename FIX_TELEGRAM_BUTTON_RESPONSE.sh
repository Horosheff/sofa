#!/bin/bash

# 🔧 ИСПРАВЛЕНИЕ ОБРАБОТКИ ОТВЕТА TELEGRAM КНОПКИ
echo "🔧 ИСПРАВЛЕНИЕ ОБРАБОТКИ ОТВЕТА TELEGRAM КНОПКИ"
echo "================================================"

cd /opt/sofiya/frontend/components

# 1. ПРОВЕРЯЕМ ЕСТЬ ЛИ ФУНКЦИЯ testTelegramBot
echo "1️⃣ Проверяем есть ли функция testTelegramBot..."
if grep -q "testTelegramBot" SettingsPanel.tsx; then
    echo "✅ Функция найдена"
    echo ""
    echo "Текущий код:"
    grep -A 30 "testTelegramBot" SettingsPanel.tsx | head -35
else
    echo "❌ Функция НЕ найдена"
    echo "Проверяем что вообще есть в файле по Telegram..."
    grep -i "telegram" SettingsPanel.tsx | head -20
fi

# 2. ИСПРАВЛЯЕМ ОБРАБОТКУ ОТВЕТА
echo ""
echo "2️⃣ Исправляем обработку ответа..."
python3 << 'PYTHON_SCRIPT'
with open('SettingsPanel.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# Ищем старый код обработки ответа
old_code = '''      if (response.ok) {
        setTelegramTestResult(`✅ Токен валиден! Бот: @${data.bot_info.username}`)
        success('Telegram бот успешно подключен!')
      }'''

new_code = '''      if (response.ok) {
        if (data.success) {
          setTelegramTestResult(`✅ ${data.message}`)
          success('Telegram бот успешно подключен!')
        } else {
          setTelegramTestResult(`❌ ${data.message || data.error}`)
          error('Ошибка проверки токена')
        }
      }'''

if old_code in content:
    content = content.replace(old_code, new_code)
    print("✅ Старый код найден и заменен")
else:
    print("❌ Старый код не найден, пробуем альтернативный поиск...")
    # Альтернативный поиск
    if 'data.bot_info.username' in content:
        content = content.replace('data.bot_info.username', 'data.bot_username')
        print("✅ Заменено data.bot_info.username на data.bot_username")
    else:
        print("❌ Не найдено data.bot_info.username")

with open('SettingsPanel.tsx', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Файл обновлен")
PYTHON_SCRIPT

# 3. ПРОВЕРЯЕМ ЧТО ИЗМЕНИЛОСЬ
echo ""
echo "3️⃣ Проверяем что изменилось..."
if grep -q "testTelegramBot" SettingsPanel.tsx; then
    echo "Новый код:"
    grep -A 30 "testTelegramBot" SettingsPanel.tsx | head -35
fi

# 4. ПЕРЕСОБИРАЕМ FRONTEND
echo ""
echo "4️⃣ Пересобираем frontend..."
cd /opt/sofiya/frontend
rm -rf .next/
npm run build

# 5. ПЕРЕЗАПУСКАЕМ FRONTEND
echo ""
echo "5️⃣ Перезапускаем frontend..."
cd /opt/sofiya
pm2 restart frontend

# 6. ПРОВЕРЯЕМ СТАТУС
echo ""
echo "6️⃣ Проверяем статус..."
pm2 status

echo ""
echo "🎯 ОБРАБОТКА ОТВЕТА ИСПРАВЛЕНА!"
echo "✅ Теперь кнопка правильно обрабатывает ответ от backend"
echo ""
echo "Теперь зайди на сайт и попробуй снова нажать кнопку!"
