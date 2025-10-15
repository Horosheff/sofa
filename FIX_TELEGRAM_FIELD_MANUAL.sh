#!/bin/bash

echo "🔧 Применяем патч для поля telegram_bot_token в SettingsPanel.tsx..."

cd /opt/sofiya/frontend/components

# Создать бэкап
cp SettingsPanel.tsx SettingsPanel.tsx.backup_$(date +%Y%m%d_%H%M%S)

# Заменить PasswordField на input с register для telegram_bot_token
python3 << 'PYTHON_SCRIPT'
import re

file_path = 'SettingsPanel.tsx'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Найти и заменить PasswordField для telegram_bot_token
old_pattern = r'<PasswordField\s+label="Токен бота"\s+name="telegram_bot_token"\s+value=\{watchValues\.telegram_bot_token\}\s+onChange=\{\(value\) => setValue\(\'telegram_bot_token\', value, \{ shouldDirty: true \}\)\}\s+placeholder="[^"]+"\s+className="[^"]+"\s+/>'

new_code = '''<div className="md:col-span-2">
              <label className="block text-sm font-medium text-foreground/80 mb-2">
                Токен бота
              </label>
              <input
                {...register('telegram_bot_token')}
                type="password"
                className="modern-input w-full"
                placeholder="123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
              />
            </div>'''

content = re.sub(old_pattern, new_code, content, flags=re.DOTALL)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Патч применён!")
PYTHON_SCRIPT

echo ""
echo "📋 Проверяем результат:"
grep -A 5 "register.*telegram_bot_token" SettingsPanel.tsx

echo ""
echo "🔄 Пересобираем frontend..."
cd /opt/sofiya/frontend
pm2 stop frontend
rm -rf .next
npm run build
pm2 start frontend

echo ""
echo "✅ Готово! Проверь в браузере (Ctrl+Shift+R для жёсткой перезагрузки)"

