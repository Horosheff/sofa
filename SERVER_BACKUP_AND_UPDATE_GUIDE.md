# 🔒 РЕЗЕРВНАЯ КОПИЯ И ОБНОВЛЕНИЕ СЕРВЕРА

## 📋 ПОШАГОВАЯ ИНСТРУКЦИЯ:

### 1️⃣ СОЗДАНИЕ РЕЗЕРВНОЙ КОПИИ

```bash
# Подключиться к серверу
ssh root@your-server-ip

# Скачать скрипт резервного копирования
cd /opt/sofiya
wget https://raw.githubusercontent.com/Horosheff/sofa/main/BACKUP_SERVER_BEFORE_UPDATE.sh

# Сделать скрипт исполняемым
chmod +x BACKUP_SERVER_BEFORE_UPDATE.sh

# Запустить резервное копирование
./BACKUP_SERVER_BEFORE_UPDATE.sh
```

### 2️⃣ ПРОВЕРКА РЕЗЕРВНОЙ КОПИИ

```bash
# Проверить созданные файлы
ls -la /opt/backups/

# Проверить размер бэкапа
du -sh /opt/backups/backup_*

# Проверить содержимое
tar -tzf /opt/backups/backup_*.tar.gz | head -20
```

### 3️⃣ ОБНОВЛЕНИЕ КОДА

```bash
# Перейти в папку проекта
cd /opt/sofiya

# Создать резервную копию текущего состояния
git bundle create /opt/backups/current_state.bundle --all

# Обновить код с GitHub
git pull origin main

# Проверить изменения
git log --oneline -5
```

### 4️⃣ УСТАНОВКА ЗАВИСИМОСТЕЙ

```bash
# Активировать виртуальное окружение
cd /opt/sofiya/backend
source venv/bin/activate

# Установить новую зависимость
pip install python-telegram-bot

# Проверить установку
pip list | grep telegram
```

### 5️⃣ МИГРАЦИЯ БАЗЫ ДАННЫХ

```bash
# Запустить миграцию
python migrate_telegram_fields.py

# Проверить структуру базы данных
sqlite3 app.db ".schema user_settings"
```

### 6️⃣ ПЕРЕЗАПУСК СЕРВИСОВ

```bash
# Перезапустить backend
pm2 restart backend

# Пересобрать frontend
cd /opt/sofiya/frontend
npm run build
pm2 restart frontend

# Проверить статус
pm2 status
```

### 7️⃣ ПРОВЕРКА РАБОТОСПОСОБНОСТИ

```bash
# Проверить логи backend
pm2 logs backend --lines 20

# Проверить логи frontend  
pm2 logs frontend --lines 20

# Проверить доступность сайта
curl -I https://mcp-kv.ru
```

## 🆘 ВОССТАНОВЛЕНИЕ ПРИ ПРОБЛЕМАХ

### Если что-то пошло не так:

```bash
# 1. Остановить все процессы
pm2 stop all

# 2. Восстановить код из бэкапа
cd /opt
tar -xzf /opt/backups/backup_*/sofiya_backup.tar.gz

# 3. Восстановить базу данных
cp /opt/backups/backup_*/app.db /opt/sofiya/backend/app.db

# 4. Восстановить PM2 конфигурацию
pm2 resurrect /opt/backups/backup_*/pm2_dump.pm2

# 5. Перезапустить все
pm2 restart all
```

## 📊 МОНИТОРИНГ ПОСЛЕ ОБНОВЛЕНИЯ

### Проверка Telegram функций:

1. **Зайти на сайт**: https://mcp-kv.ru
2. **Перейти в Настройки**: Найти секцию "🤖 Telegram Bot настройки"
3. **Создать бота**: Через @BotFather в Telegram
4. **Вставить токен**: В настройки и сохранить
5. **Перейти в Инструменты**: Найти секцию "🤖 Telegram"
6. **Протестировать**: Любой Telegram инструмент

### Проверка логов:

```bash
# Следить за логами в реальном времени
pm2 logs backend --lines 0

# Проверить ошибки
pm2 logs backend --err --lines 50
pm2 logs frontend --err --lines 50
```

## 🔧 ДОПОЛНИТЕЛЬНЫЕ КОМАНДЫ

### Очистка старых бэкапов:
```bash
# Удалить бэкапы старше 7 дней
find /opt/backups -name "backup_*" -type d -mtime +7 -exec rm -rf {} \;
```

### Проверка места на диске:
```bash
# Проверить использование диска
df -h

# Проверить размер бэкапов
du -sh /opt/backups/*
```

### Создание быстрого бэкапа:
```bash
# Быстрый бэкап только базы данных
cp /opt/sofiya/backend/app.db /opt/backups/quick_backup_$(date +%H%M%S).db
```

## ✅ ЧЕКЛИСТ ПЕРЕД ОБНОВЛЕНИЕМ

- [ ] Создана полная резервная копия
- [ ] Проверен размер бэкапа
- [ ] Сохранена текущая версия в Git
- [ ] Проверена доступность GitHub
- [ ] Подготовлен план отката
- [ ] Уведомлены пользователи (если нужно)

## 🎯 ОЖИДАЕМЫЙ РЕЗУЛЬТАТ

После успешного обновления:
- ✅ Сайт работает без ошибок
- ✅ Telegram настройки доступны в панели
- ✅ Telegram инструменты работают
- ✅ Все сервисы запущены (PM2 green)
- ✅ Логи без критических ошибок

**Готово к обновлению! 🚀**
