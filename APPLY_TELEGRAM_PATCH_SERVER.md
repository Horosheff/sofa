# 🚀 ПРИМЕНЕНИЕ TELEGRAM ПАТЧА НА СЕРВЕРЕ

## 📋 Команды для сервера:

### 1. Обновление кода
```bash
cd /opt/sofiya
git pull origin main
```

### 2. Установка зависимостей
```bash
cd /opt/sofiya/backend
source venv/bin/activate
pip install python-telegram-bot
```

### 3. Миграция базы данных
```bash
cd /opt/sofiya/backend
python migrate_telegram_fields.py
```

### 4. Перезапуск backend
```bash
pm2 restart backend
```

### 5. Пересборка frontend
```bash
cd /opt/sofiya/frontend
npm run build
pm2 restart frontend
```

### 6. Проверка статуса
```bash
pm2 status
pm2 logs backend --lines 20
pm2 logs frontend --lines 20
```

## ✅ Ожидаемый результат:

- **Backend**: Telegram инструменты доступны в MCP
- **Frontend**: Настройки Telegram в панели настроек
- **Database**: Новые поля для Telegram настроек
- **Status**: Все сервисы работают (green)

## 🔧 Проверка работы:

1. Зайти на сайт https://mcp-kv.ru
2. Перейти в **Настройки**
3. Найти секцию **🤖 Telegram Bot настройки**
4. Создать бота через @BotFather
5. Вставить токен и сохранить
6. Перейти в **Инструменты**
7. Найти секцию **🤖 Telegram**
8. Протестировать инструменты

## 🆘 Если что-то не работает:

```bash
# Проверить логи
pm2 logs backend --err --lines 50
pm2 logs frontend --err --lines 50

# Перезапустить все
pm2 restart all

# Проверить базу данных
cd /opt/sofiya/backend
python -c "import sqlite3; conn = sqlite3.connect('app.db'); print(conn.execute('PRAGMA table_info(user_settings)').fetchall())"
```

**Готово! Telegram интеграция применена на сервере! 🎉**
