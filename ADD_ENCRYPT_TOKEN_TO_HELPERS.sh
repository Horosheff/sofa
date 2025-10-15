#!/bin/bash

# 🔐 ДОБАВЛЕНИЕ ФУНКЦИИ encrypt_token В HELPERS.PY
echo "🔐 ДОБАВЛЕНИЕ ФУНКЦИИ encrypt_token В HELPERS.PY"
echo "================================================"

cd /opt/sofiya/backend/app

# 1. СОЗДАЕМ БЭКАП
echo "1️⃣ Создаем бэкап helpers.py..."
cp helpers.py helpers.py.backup_encrypt_$(date +%Y%m%d_%H%M%S)

# 2. ДОБАВЛЯЕМ ФУНКЦИИ ШИФРОВАНИЯ
echo "2️⃣ Добавляем функции шифрования..."
python3 << 'PYTHON_SCRIPT'
with open('helpers.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Добавляем импорты для шифрования в начало файла
imports_to_add = '''import os
from cryptography.fernet import Fernet
'''

# Проверяем есть ли уже эти импорты
if 'from cryptography.fernet import Fernet' not in content:
    # Добавляем после существующих импортов
    content = content.replace(
        'import logging\n',
        'import logging\n' + imports_to_add
    )
    print("✅ Добавлены импорты для шифрования")
else:
    print("✅ Импорты уже есть")

# Добавляем функции шифрования в конец файла
encryption_functions = '''

# ==================== ENCRYPTION / DECRYPTION ====================

# Получаем ключ шифрования из переменных окружения
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY") or os.getenv("FERNET_KEY")

if not ENCRYPTION_KEY:
    logger.warning("⚠️  ENCRYPTION_KEY не установлен! Создаем временный ключ...")
    # Генерируем временный ключ если не установлен
    ENCRYPTION_KEY = Fernet.generate_key().decode('utf-8')
    logger.warning(f"⚠️  Временный ключ: {ENCRYPTION_KEY}")
    logger.warning("⚠️  Установите ENCRYPTION_KEY в переменные окружения!")

cipher_suite = Fernet(ENCRYPTION_KEY.encode('utf-8') if isinstance(ENCRYPTION_KEY, str) else ENCRYPTION_KEY)


def encrypt_token(token: str) -> str:
    """
    Шифрование токена
    
    Args:
        token: Токен для шифрования
    
    Returns:
        Зашифрованный токен (str)
    """
    if not token:
        return token
    
    try:
        encrypted = cipher_suite.encrypt(token.encode('utf-8'))
        return encrypted.decode('utf-8')
    except Exception as e:
        logger.error(f"Ошибка шифрования токена: {e}")
        raise ValueError(f"Не удалось зашифровать токен: {e}")


def decrypt_token(encrypted_token: str) -> str:
    """
    Расшифровка токена
    
    Args:
        encrypted_token: Зашифрованный токен
    
    Returns:
        Расшифрованный токен (str)
    """
    if not encrypted_token:
        return encrypted_token
    
    try:
        decrypted = cipher_suite.decrypt(encrypted_token.encode('utf-8'))
        return decrypted.decode('utf-8')
    except Exception as e:
        logger.error(f"Ошибка расшифровки токена: {e}")
        raise ValueError(f"Не удалось расшифровать токен: {e}")
'''

# Добавляем функции в конец файла
if 'def encrypt_token' not in content:
    content += encryption_functions
    print("✅ Добавлены функции encrypt_token и decrypt_token")
else:
    print("✅ Функции шифрования уже есть")

with open('helpers.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Файл helpers.py обновлен")
PYTHON_SCRIPT

# 3. ПРОВЕРЯЕМ ЧТО ФУНКЦИИ ДОБАВЛЕНЫ
echo ""
echo "3️⃣ Проверяем что функции добавлены..."
if grep -q "def encrypt_token" helpers.py && grep -q "def decrypt_token" helpers.py; then
    echo "✅ Функции encrypt_token и decrypt_token найдены"
else
    echo "❌ Функции не найдены"
    exit 1
fi

# 4. УСТАНАВЛИВАЕМ CRYPTOGRAPHY
echo ""
echo "4️⃣ Устанавливаем cryptography..."
cd /opt/sofiya/backend
source venv/bin/activate
pip install cryptography

# 5. ПЕРЕЗАПУСКАЕМ BACKEND
echo ""
echo "5️⃣ Перезапускаем backend..."
cd /opt/sofiya
pm2 restart backend

# 6. ЖДЕМ ЗАПУСКА
echo "6️⃣ Ждем запуска..."
sleep 5

# 7. ПРОВЕРЯЕМ СТАТУС
echo "7️⃣ Проверяем статус..."
pm2 status

# 8. ПРОВЕРЯЕМ ЛОГИ
echo "8️⃣ Проверяем логи..."
pm2 logs backend --lines 15 --nostream

echo ""
echo "🎯 ФУНКЦИИ ШИФРОВАНИЯ ДОБАВЛЕНЫ!"
echo "✅ encrypt_token добавлен в helpers.py"
echo "✅ decrypt_token добавлен в helpers.py"
echo "✅ cryptography установлен"
echo "✅ Backend перезапущен"
echo ""
echo "Теперь можно сохранять токены - они будут зашифрованы!"
