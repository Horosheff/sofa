#!/bin/bash
# Скрипт для уменьшения количества Telegram инструментов с 66 до 32

echo "🗑️  УМЕНЬШЕНИЕ TELEGRAM ИНСТРУМЕНТОВ: 66 → 32"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

cd /opt/sofiya

# Создаем резервную копию
cp backend/app/mcp_handlers.py backend/app/mcp_handlers.py.backup_$(date +%Y%m%d_%H%M%S)
echo "✅ Создана резервная копия"

# Скачиваем новую версию функции
wget -q https://raw.githubusercontent.com/Horosheff/sofa/main/telegram_tools_minimal.py -O /tmp/telegram_tools_minimal.py
echo "📥 Загружена новая версия функции"

# Создаем Python скрипт для замены
cat > /tmp/replace_telegram_tools.py << 'PYTHON_SCRIPT'
#!/usr/bin/env python3
import re

# Читаем новую функцию
with open('/tmp/telegram_tools_minimal.py', 'r', encoding='utf-8') as f:
    new_function = f.read()

# Читаем основной файл
with open('backend/app/mcp_handlers.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Ищем и заменяем функцию get_telegram_tools
pattern = r'def get_telegram_tools\(\) -> list:.*?(?=\n\ndef )'
match = re.search(pattern, content, re.DOTALL)

if match:
    print(f"✅ Найдена функция get_telegram_tools (длина: {len(match.group(0))} символов)")
    content = content[:match.start()] + new_function.strip() + '\n' + content[match.end():]
    print("✅ Функция заменена на минимальную версию")
else:
    print("❌ Функция get_telegram_tools не найдена!")
    exit(1)

# Записываем обратно
with open('backend/app/mcp_handlers.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Файл обновлен!")

PYTHON_SCRIPT

# Запускаем Python скрипт
python3 /tmp/replace_telegram_tools.py

# Удаляем временные файлы
rm /tmp/telegram_tools_minimal.py
rm /tmp/replace_telegram_tools.py

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ ПАТЧ ПРИМЕНЕН!"
echo ""

# Проверяем количество инструментов
cd backend
source venv/bin/activate
echo "📊 Проверяем количество инструментов:"
python3 -c "from app.mcp_handlers import get_telegram_tools, get_all_mcp_tools; print(f'Telegram: {len(get_telegram_tools())} инструментов'); print(f'Всего: {len(get_all_mcp_tools())} инструментов')"

echo ""
echo "🔄 Перезапускаем backend..."
pm2 restart backend

echo ""
echo "✅ ГОТОВО! Telegram инструментов сокращено с 66 до 32"

