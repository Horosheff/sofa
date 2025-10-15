#!/bin/bash
# Восстановить кнопку проверки Telegram токена в SettingsPanel.tsx

echo "🔄 ВОССТАНОВЛЕНИЕ КНОПКИ ПРОВЕРКИ TELEGRAM ТОКЕНА"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

cd /opt/sofiya/frontend

# Создать резервную копию
cp components/SettingsPanel.tsx components/SettingsPanel.tsx.backup_$(date +%Y%m%d_%H%M%S)
echo "✅ Создана резервная копия SettingsPanel.tsx"

# Создать Python скрипт для добавления функции и кнопки
cat > /tmp/add_telegram_button.py << 'PYTHON_SCRIPT'
#!/usr/bin/env python3

# Читаем файл
with open('components/SettingsPanel.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# Проверяем, есть ли уже функция
if 'testTelegramBot' in content:
    print("✅ Кнопка уже есть")
    exit(0)

# 1. Добавляем state для Telegram теста после других useState
state_addition = '''  const [telegramTestResult, setTelegramTestResult] = useState<string | null>(null)
  const [isTelegramTesting, setIsTelegramTesting] = useState(false)
'''

# Находим место после последнего useState
import re
last_usestate = list(re.finditer(r'const \[.*?\] = useState', content))[-1]
insert_pos = content.find('\n', last_usestate.end()) + 1
content = content[:insert_pos] + state_addition + content[insert_pos:]

# 2. Добавляем функцию testTelegramBot после onSubmit
function_addition = '''
  const testTelegramBot = async () => {
    setIsTelegramTesting(true)
    setTelegramTestResult(null)
    try {
      // 1. Сохранить токен
      await handleSubmit(onSubmit)()

      // 2. Проверить токен
      const response = await fetch('/telegram/check-token', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
      })
      const data = await response.json()

      if (response.ok) {
        setTelegramTestResult(data.message)
        success(data.message)
      } else {
        setTelegramTestResult(data.detail || data.message || 'Неизвестная ошибка')
        error(data.detail || data.message || 'Неизвестная ошибка')
      }
    } catch (err: any) {
      console.error('Ошибка проверки Telegram токена:', err)
      setTelegramTestResult(`Ошибка проверки: ${err.message}`)
      error(`Ошибка проверки: ${err.message}`)
    } finally {
      setIsTelegramTesting(false)
    }
  }
'''

# Находим конец функции onSubmit
onsubmit_match = re.search(r'const onSubmit = async.*?\n  \}', content, re.DOTALL)
if onsubmit_match:
    insert_pos = onsubmit_match.end() + 1
    content = content[:insert_pos] + function_addition + content[insert_pos:]
    print("✅ Функция testTelegramBot добавлена")

# 3. Добавляем кнопку в секцию Telegram Bot
button_html = '''                <div className="mt-6">
                  <button
                    type="button"
                    onClick={testTelegramBot}
                    disabled={isTelegramTesting || !watchValues.telegram_bot_token}
                    className={`
                      w-full py-3 px-6 rounded-lg text-lg font-semibold
                      transition-all duration-200 ease-in-out
                      flex items-center justify-center gap-3
                      ${isTelegramTesting
                        ? 'bg-gray-500 cursor-not-allowed'
                        : 'bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 active:scale-95 shadow-lg hover:shadow-xl'
                      }
                    `}
                  >
                    {isTelegramTesting ? (
                      <>
                        <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        Проверка...
                      </>
                    ) : (
                      <>
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                          <path strokeLinecap="round" strokeLinejoin="round" d="M15 13l-3 3m0 0l-3-3m3 3V8m0 13a9 9 0 110-18 9 9 0 010 18z" />
                        </svg>
                        Проверить токен бота
                      </>
                    )}
                  </button>
                  {telegramTestResult && (
                    <div className={`
                      mt-4 p-4 rounded-lg border-l-4
                      ${telegramTestResult.startsWith('✅') ? 'bg-green-100 border-green-500 text-green-800' : 'bg-red-100 border-red-500 text-red-800'}
                      flex items-center gap-3
                    `}>
                      {telegramTestResult.startsWith('✅') ? (
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                          <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                      ) : (
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                          <path strokeLinecap="round" strokeLinejoin="round" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                      )}
                      <p className="text-sm font-medium">{telegramTestResult}</p>
                    </div>
                  )}
                </div>
'''

# Находим закрывающий div секции Telegram (после последнего PasswordField для telegram_webhook_secret)
telegram_section = re.search(r'<PasswordField[^>]*name="telegram_webhook_secret"[^/]*/>.*?\n\s*</div>', content, re.DOTALL)
if telegram_section:
    insert_pos = content.find('</div>', telegram_section.end() - 10)
    content = content[:insert_pos] + button_html + '\n              ' + content[insert_pos:]
    print("✅ Кнопка добавлена в UI")

# Записываем обратно
with open('components/SettingsPanel.tsx', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Патч применен!")
PYTHON_SCRIPT

# Запустить Python скрипт
python3 /tmp/add_telegram_button.py

# Удалить временный файл
rm /tmp/add_telegram_button.py

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ ПАТЧ ПРИМЕНЕН!"
echo ""
echo "🔄 Пересобираем frontend..."
pm2 stop frontend
rm -rf .next
npm run build
pm2 start frontend

echo ""
echo "✅ ГОТОВО! Кнопка проверки Telegram токена восстановлена!"

