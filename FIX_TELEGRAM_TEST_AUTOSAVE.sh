#!/bin/bash

# 🔧 ИСПРАВЛЕНИЕ: АВТОСОХРАНЕНИЕ ТОКЕНА ПЕРЕД ПРОВЕРКОЙ
echo "🔧 ИСПРАВЛЕНИЕ: АВТОСОХРАНЕНИЕ ТОКЕНА ПЕРЕД ПРОВЕРКОЙ"
echo "======================================================"

cd /opt/sofiya/frontend/components

# 1. СОЗДАЕМ БЭКАП
echo "1️⃣ Создаем бэкап SettingsPanel.tsx..."
cp SettingsPanel.tsx SettingsPanel.tsx.backup_autosave_$(date +%Y%m%d_%H%M%S)

# 2. ИЗМЕНЯЕМ ФУНКЦИЮ testTelegramBot
echo "2️⃣ Изменяем функцию testTelegramBot для автосохранения..."
python3 << 'PYTHON_SCRIPT'
import re

with open('SettingsPanel.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# Ищем функцию testTelegramBot
old_function_pattern = r'const testTelegramBot = async \(\) => \{[^}]+\{[^}]+\}[^}]+\}'

# Новая функция с автосохранением
new_function = '''const testTelegramBot = async () => {
    if (!token) {
      error('Необходима авторизация')
      return
    }
    
    const currentToken = watchValues.telegram_bot_token
    if (!currentToken || !currentToken.trim()) {
      error('Введите токен Telegram бота')
      return
    }
    
    setIsTelegramTesting(true)
    setTelegramTestResult('')
    
    try {
      // 1. СНАЧАЛА СОХРАНЯЕМ ТОКЕН
      const settingsToSave = getValues()
      
      const saveResponse = await fetch('/api/user/settings', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(settingsToSave)
      })
      
      if (!saveResponse.ok) {
        throw new Error('Не удалось сохранить настройки')
      }
      
      // 2. ТЕПЕРЬ ПРОВЕРЯЕМ ТОКЕН
      const response = await fetch('/api/telegram/check-token', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      })
      
      const data = await response.json()
      
      if (response.ok) {
        if (data.success) {
          setTelegramTestResult(`✅ ${data.message}`)
          success('Telegram бот успешно подключен!')
        } else {
          setTelegramTestResult(`❌ ${data.message || data.error}`)
          error('Ошибка проверки токена')
        }
      } else {
        setTelegramTestResult(`❌ Ошибка: ${data.detail}`)
        error('Ошибка проверки токена')
      }
    } catch (err) {
      console.error('Ошибка проверки Telegram токена:', err)
      setTelegramTestResult('❌ Ошибка соединения с сервером')
      error('Ошибка проверки токена')
    } finally {
      setIsTelegramTesting(false)
    }
  }'''

# Ищем и заменяем функцию
if 'const testTelegramBot = async' in content:
    # Находим начало функции
    start = content.find('const testTelegramBot = async')
    if start != -1:
        # Находим конец функции (закрывающая фигурная скобка на том же уровне отступа)
        indent_level = 0
        end = start
        in_function = False
        
        for i in range(start, len(content)):
            if content[i] == '{':
                indent_level += 1
                in_function = True
            elif content[i] == '}':
                indent_level -= 1
                if in_function and indent_level == 0:
                    end = i + 1
                    break
        
        if end > start:
            # Заменяем старую функцию на новую
            content = content[:start] + new_function + content[end:]
            print("✅ Функция testTelegramBot обновлена")
        else:
            print("❌ Не удалось найти конец функции")
    else:
        print("❌ Не удалось найти функцию testTelegramBot")
else:
    print("❌ Функция testTelegramBot не найдена")

with open('SettingsPanel.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
PYTHON_SCRIPT

# 3. ПЕРЕСОБИРАЕМ FRONTEND
echo ""
echo "3️⃣ Пересобираем frontend..."
cd /opt/sofiya/frontend
rm -rf .next/
npm run build

# 4. ПЕРЕЗАПУСКАЕМ FRONTEND
echo ""
echo "4️⃣ Перезапускаем frontend..."
cd /opt/sofiya
pm2 restart frontend

# 5. ПРОВЕРЯЕМ СТАТУС
echo ""
echo "5️⃣ Проверяем статус..."
pm2 status

echo ""
echo "🎯 АВТОСОХРАНЕНИЕ ТОКЕНА ДОБАВЛЕНО!"
echo "✅ Теперь при нажатии 'Проверить токен':"
echo "   1. Токен сначала СОХРАНЯЕТСЯ в БД"
echo "   2. Потом ПРОВЕРЯЕТСЯ через Telegram API"
echo ""
echo "Теперь можно просто ввести токен и сразу нажать 'Проверить'!"
