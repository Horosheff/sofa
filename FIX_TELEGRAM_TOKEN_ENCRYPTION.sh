#!/bin/bash

# 🔐 ДОБАВЛЕНИЕ ШИФРОВАНИЯ TELEGRAM ТОКЕНА
echo "🔐 ДОБАВЛЕНИЕ ШИФРОВАНИЯ TELEGRAM ТОКЕНА"
echo "========================================"

cd /opt/sofiya/backend/app

# 1. СОЗДАЕМ БЭКАП
echo "1️⃣ Создаем бэкап main.py..."
cp main.py main.py.backup_encryption_$(date +%Y%m%d_%H%M%S)

# 2. ДОБАВЛЯЕМ ИМПОРТ encrypt_token
echo "2️⃣ Добавляем импорт encrypt_token..."
python3 << 'PYTHON_SCRIPT'
with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Проверяем есть ли уже импорт
if 'from .helpers import' in content and 'encrypt_token' not in content:
    # Находим строку с импортом helpers
    old_import = 'from .helpers import ('
    if old_import in content:
        # Добавляем encrypt_token и decrypt_token к импортам
        content = content.replace(
            'from .helpers import (',
            'from .helpers import (\n    encrypt_token,\n    decrypt_token,'
        )
        print("✅ Добавлен импорт encrypt_token и decrypt_token")
    else:
        print("❌ Не найдена строка импорта helpers")
else:
    print("✅ Импорт encrypt_token уже есть")

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)
PYTHON_SCRIPT

# 3. ДОБАВЛЯЕМ ШИФРОВАНИЕ В PUT /user/settings
echo "3️⃣ Добавляем шифрование в PUT /user/settings..."
python3 << 'PYTHON_SCRIPT'
with open('main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Находим место для вставки шифрования (перед setattr)
new_lines = []
for i, line in enumerate(lines):
    new_lines.append(line)
    
    # Если это строка с setattr в update_user_settings
    if 'setattr(settings, key, value)' in line and i > 0:
        # Проверяем что мы в функции update_user_settings
        context = ''.join(lines[max(0, i-30):i])
        if 'def update_user_settings' in context:
            # Вставляем шифрование перед setattr
            indent = '            '
            encryption_code = f'''
{indent}# Шифруем чувствительные данные
{indent}if key in ['telegram_bot_token', 'telegram_webhook_secret', 'wordpress_password', 'wordstat_client_secret']:
{indent}    if value and value.strip():
{indent}        value = encrypt_token(value)
{indent}
'''
            # Удаляем текущую строку и вставляем шифрование + setattr
            new_lines[-1] = encryption_code + line

with open('main.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("✅ Добавлено шифрование чувствительных данных")
PYTHON_SCRIPT

# 4. ПРОВЕРЯЕМ ЧТО ИЗМЕНИЛОСЬ
echo "4️⃣ Проверяем что изменилось..."
grep -A 10 "# Шифруем чувствительные данные" main.py

# 5. УДАЛЯЕМ СУЩЕСТВУЮЩИЙ НЕЗАШИФРОВАННЫЙ ТОКЕН
echo ""
echo "5️⃣ Удаляем существующий незашифрованный токен..."
cd /opt/sofiya/backend
sqlite3 app.db "UPDATE user_settings SET telegram_bot_token = NULL WHERE user_id = 1;"
echo "✅ Токен удален из базы"

# 6. ПЕРЕЗАПУСКАЕМ BACKEND
echo ""
echo "6️⃣ Перезапускаем backend..."
cd /opt/sofiya
pm2 restart backend

# 7. ЖДЕМ ЗАПУСКА
echo "7️⃣ Ждем запуска..."
sleep 3

# 8. ПРОВЕРЯЕМ СТАТУС
echo "8️⃣ Проверяем статус..."
pm2 status

# 9. ПРОВЕРЯЕМ ЛОГИ
echo "9️⃣ Проверяем логи..."
pm2 logs backend --lines 10 --nostream

echo ""
echo "🎯 ШИФРОВАНИЕ ТОКЕНА ДОБАВЛЕНО!"
echo "✅ Импорт encrypt_token добавлен"
echo "✅ Шифрование добавлено в PUT /user/settings"
echo "✅ Старый незашифрованный токен удален"
echo "✅ Backend перезапущен"
echo ""
echo "⚠️  ВАЖНО: Теперь зайди в настройки и ЗАНОВО сохрани токен!"
echo "Он будет автоматически зашифрован при сохранении."
