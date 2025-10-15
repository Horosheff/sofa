# 🗑️ Уменьшение Telegram инструментов с 66 до 32

## 📊 Что убирается:

### ❌ Удаляется (34 инструмента):
- `telegram_create_bot` - создание бота (заменено на прямой ввод токена)
- Все инструменты управления чатами (15 шт): ban, unban, promote, restrict, kick, set_photo, set_title, set_description и т.д.
- Все инструменты закрепления сообщений в чатах (6 шт): pin_chat_message, unpin_chat_message и т.д.
- Все инструменты приглашений (6 шт): export_invite_link, create_invite_link, revoke_invite_link и т.д.
- Все инструменты стикеров (7 шт): send_sticker, get_sticker_set, create_sticker_set и т.д.

### ✅ Остается (32 инструмента):
- Отправка сообщений и медиа (11 шт)
- Управление сообщениями (4 шт): delete, edit, pin, unpin
- Webhook и обновления (4 шт)
- Команды бота (2 шт)
- Опросы (2 шт)
- Callback и inline queries (2 шт)
- Игры и платежи (2 шт)
- Файлы и профили (2 шт)
- Действия чата (1 шт)

## 🚀 Применение на сервере:

```bash
# 1. Подключиться к серверу
ssh root@your-server

# 2. Перейти в папку проекта
cd /opt/sofiya

# 3. Сохранить текущие изменения
git stash push -m "local_changes_before_telegram_reduction_$(date +%Y%m%d_%H%M%S)"

# 4. Обновить код
git pull origin main

# 5. Скачать и запустить скрипт
wget -q https://raw.githubusercontent.com/Horosheff/sofa/main/REDUCE_TELEGRAM_TOOLS_v2.sh
chmod +x REDUCE_TELEGRAM_TOOLS_v2.sh
./REDUCE_TELEGRAM_TOOLS_v2.sh

# 6. Проверить результат
cd /opt/sofiya/backend
source venv/bin/activate
python3 -c "from app.mcp_handlers import get_telegram_tools, get_all_mcp_tools; print(f'Telegram: {len(get_telegram_tools())}'); print(f'Всего: {len(get_all_mcp_tools())}')"
```

## ✅ Ожидаемый результат:

```
Telegram: 32
Всего: 65 (28 WordPress + 5 Wordstat + 32 Telegram)
```

## 📋 Проверка в ChatGPT:

После применения патча ChatGPT должен увидеть **65 инструментов** вместо 99.

## 🔄 Если что-то пошло не так:

```bash
# Восстановить из резервной копии
cd /opt/sofiya/backend
ls -la app/mcp_handlers.py.backup_*
cp app/mcp_handlers.py.backup_YYYYMMDD_HHMMSS app/mcp_handlers.py
pm2 restart backend
```

---

**Патч готов к применению!** ✅

