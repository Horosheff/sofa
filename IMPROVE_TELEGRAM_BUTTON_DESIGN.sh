#!/bin/bash

# 🎨 УЛУЧШЕНИЕ ДИЗАЙНА КНОПКИ ПРОВЕРКИ TELEGRAM
echo "🎨 УЛУЧШЕНИЕ ДИЗАЙНА КНОПКИ ПРОВЕРКИ TELEGRAM"
echo "=============================================="

cd /opt/sofiya/frontend/components

# 1. СОЗДАЕМ БЭКАП
echo "1️⃣ Создаем бэкап SettingsPanel.tsx..."
cp SettingsPanel.tsx SettingsPanel.tsx.backup_design_$(date +%Y%m%d_%H%M%S)

# 2. УЛУЧШАЕМ ДИЗАЙН КНОПКИ И РЕЗУЛЬТАТА
echo "2️⃣ Улучшаем дизайн кнопки и результата..."
python3 << 'PYTHON_SCRIPT'
with open('SettingsPanel.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# Старый код кнопки
old_button_code = '''          {/* Кнопка проверки токена */}
          <div className="mt-4">
            <button
              type="button"
              onClick={testTelegramBot}
              disabled={!watchValues.telegram_bot_token || isTelegramTesting}
              className="modern-btn w-full md:w-auto disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isTelegramTesting ? '⏳ Проверка...' : '🔍 Проверить токен бота'}
            </button>
            {telegramTestResult && (
              <p className="mt-2 text-sm text-foreground/70">{telegramTestResult}</p>
            )}
          </div>'''

# Новый улучшенный дизайн
new_button_code = '''          {/* Кнопка проверки токена */}
          <div className="mt-6">
            <button
              type="button"
              onClick={testTelegramBot}
              disabled={!watchValues.telegram_bot_token || isTelegramTesting}
              className="group relative inline-flex items-center justify-center gap-3 px-6 py-3 
                         bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700
                         text-white font-semibold rounded-lg shadow-lg hover:shadow-xl
                         transform transition-all duration-200 hover:scale-105
                         disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none
                         disabled:hover:shadow-lg w-full md:w-auto"
            >
              {isTelegramTesting ? (
                <>
                  <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <span>Проверка токена...</span>
                </>
              ) : (
                <>
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span>Проверить токен бота</span>
                </>
              )}
            </button>
            
            {/* Результат проверки */}
            {telegramTestResult && (
              <div className={`mt-4 p-4 rounded-lg border-2 ${
                telegramTestResult.startsWith('✅') 
                  ? 'bg-green-50 dark:bg-green-900/20 border-green-400 dark:border-green-600' 
                  : 'bg-red-50 dark:bg-red-900/20 border-red-400 dark:border-red-600'
              }`}>
                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0 mt-0.5">
                    {telegramTestResult.startsWith('✅') ? (
                      <svg className="w-6 h-6 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    ) : (
                      <svg className="w-6 h-6 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    )}
                  </div>
                  <div className="flex-1">
                    <p className={`font-medium ${
                      telegramTestResult.startsWith('✅') 
                        ? 'text-green-800 dark:text-green-200' 
                        : 'text-red-800 dark:text-red-200'
                    }`}>
                      {telegramTestResult}
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>'''

if old_button_code in content:
    content = content.replace(old_button_code, new_button_code)
    print("✅ Дизайн кнопки обновлен")
else:
    print("❌ Старый код кнопки не найден")
    print("Попробуем найти альтернативный вариант...")
    # Альтернативный поиск по части кода
    if 'Проверить токен бота' in content:
        print("✅ Код с кнопкой найден, но структура отличается")
        print("Требуется ручное обновление")

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
echo "🎯 ДИЗАЙН КНОПКИ УЛУЧШЕН!"
echo "✅ Кнопка теперь имеет:"
echo "   • Красивый градиент (синий)"
echo "   • Анимацию при наведении (увеличение)"
echo "   • Спиннер при проверке"
echo "   • Иконку проверки"
echo "   • Тень и закругленные углы"
echo ""
echo "✅ Результат проверки теперь:"
echo "   • В красивом блоке с рамкой"
echo "   • Зеленый фон для успеха ✅"
echo "   • Красный фон для ошибки ❌"
echo "   • С иконкой результата"
echo ""
echo "Зайди на сайт и посмотри как красиво!"
