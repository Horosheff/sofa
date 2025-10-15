#!/bin/bash
# СРОЧНЫЙ ПАТЧ: Добавить decrypt_token в helpers.py

echo "🚨 СРОЧНОЕ ИСПРАВЛЕНИЕ: Добавляем decrypt_token в helpers.py"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

cd /opt/sofiya/backend

# Создаем резервную копию
cp app/helpers.py app/helpers.py.backup_$(date +%Y%m%d_%H%M%S)
echo "✅ Создана резервная копия helpers.py"

# Проверяем, есть ли уже decrypt_token
if grep -q "def decrypt_token" app/helpers.py; then
    echo "✅ decrypt_token уже существует"
    exit 0
fi

# Добавляем импорты и функции шифрования в начало файла
cat > /tmp/encryption_functions.py << 'PYTHON_CODE'
import os
from cryptography.fernet import Fernet
import logging

logger = logging.getLogger(__name__)

# Получаем ключ шифрования из переменных окружения
FERNET_KEY = os.getenv("FERNET_KEY")
if FERNET_KEY:
    try:
        cipher_suite = Fernet(FERNET_KEY.encode('utf-8'))
        logger.info("✅ Ключ шифрования загружен")
    except Exception as e:
        logger.error(f"❌ Ошибка загрузки ключа шифрования: {e}")
        cipher_suite = None
else:
    logger.warning("⚠️  FERNET_KEY не установлен. Шифрование/расшифровка недоступны.")
    cipher_suite = None

def encrypt_token(token: str) -> str:
    """
    Зашифровать токен
    
    Args:
        token: Токен для шифрования
    
    Returns:
        Зашифрованный токен
    """
    if not cipher_suite:
        raise ValueError("Ключ шифрования не установлен. Невозможно зашифровать токен.")
    if not token:
        return token
    try:
        return cipher_suite.encrypt(token.encode('utf-8')).decode('utf-8')
    except Exception as e:
        logger.error(f"Ошибка шифрования токена: {e}")
        raise

def decrypt_token(encrypted_token: str) -> str:
    """
    Расшифровать токен
    
    Args:
        encrypted_token: Зашифрованный токен
    
    Returns:
        Расшифрованный токен
    """
    if not cipher_suite:
        raise ValueError("Ключ шифрования не установлен. Невозможно расшифровать токен.")
    if not encrypted_token:
        return encrypted_token
    try:
        return cipher_suite.decrypt(encrypted_token.encode('utf-8')).decode('utf-8')
    except Exception as e:
        logger.error(f"Ошибка расшифровки токена: {e}")
        raise

PYTHON_CODE

# Добавляем функции в начало helpers.py (после существующих импортов)
python3 << 'PYTHON_SCRIPT'
# Читаем существующий файл
with open('app/helpers.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Читаем новые функции
with open('/tmp/encryption_functions.py', 'r', encoding='utf-8') as f:
    encryption_code = f.read()

# Проверяем, есть ли уже импорт logging
if 'import logging' not in content:
    # Добавляем импорт logging в начало
    content = "import logging\n" + content

# Находим место после всех импортов
import_end = 0
for i, line in enumerate(content.split('\n')):
    if line.startswith('import ') or line.startswith('from '):
        import_end = i + 1
    elif line.strip() and not line.startswith('#'):
        break

lines = content.split('\n')
# Вставляем код шифрования после импортов
lines.insert(import_end, '\n' + encryption_code + '\n')

# Записываем обратно
with open('app/helpers.py', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

print("✅ Функции шифрования добавлены в helpers.py")
PYTHON_SCRIPT

# Удаляем временный файл
rm /tmp/encryption_functions.py

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ ПАТЧ ПРИМЕНЕН!"
echo ""

# Проверяем, что функции добавлены
if grep -q "def decrypt_token" app/helpers.py; then
    echo "✅ decrypt_token найден в helpers.py"
else
    echo "❌ ОШИБКА: decrypt_token не найден!"
    exit 1
fi

# Устанавливаем cryptography если не установлен
source venv/bin/activate
pip list | grep cryptography > /dev/null
if [ $? -ne 0 ]; then
    echo "📦 Устанавливаем cryptography..."
    pip install cryptography
else
    echo "✅ cryptography уже установлен"
fi

# Проверяем FERNET_KEY
if [ -z "$FERNET_KEY" ]; then
    echo "⚠️  WARNING: FERNET_KEY не установлен!"
    echo "Запустите: source SET_ENCRYPTION_KEY.sh"
fi

echo ""
echo "🔄 Перезапускаем backend..."
pm2 restart backend

echo ""
echo "✅ ГОТОВО!"

