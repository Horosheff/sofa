# 🚀 Руководство по развертыванию WordPress MCP Platform

## 📋 Подготовка к развертыванию

### 1. Обновленные файлы готовы:
- ✅ `docker-compose.yml` - конфигурация сервисов
- ✅ `frontend/Dockerfile` - образ frontend
- ✅ `frontend/next.config.js` - конфигурация Next.js
- ✅ `backend/init_db.py` - инициализация базы данных
- ✅ `deploy.sh` - скрипт полного развертывания
- ✅ `quick-deploy.sh` - скрипт быстрого обновления
- ✅ `upload-to-server.sh` - скрипт передачи файлов
- ✅ `README.md` - документация проекта

## 🖥️ Развертывание на сервере

### Вариант 1: Полное развертывание (рекомендуется)

```bash
# 1. Передача файлов на сервер
./upload-to-server.sh root@89.40.233.33

# 2. Подключение к серверу и развертывание
ssh root@89.40.233.33
cd /root/sofiya
./deploy.sh
```

### Вариант 2: Быстрое обновление (если уже развернуто)

```bash
# 1. Передача файлов
./upload-to-server.sh root@89.40.233.33

# 2. Быстрое обновление
ssh root@89.40.233.33
cd /root/sofiya
./quick-deploy.sh
```

## 🔧 Ручное развертывание

Если скрипты не работают, выполните команды вручную:

```bash
# Подключение к серверу
ssh root@89.40.233.33

# Переход в директорию проекта
cd /root/sofiya

# Остановка существующих контейнеров
docker-compose down

# Очистка старых образов
docker system prune -f

# Сборка новых образов
docker-compose build --no-cache

# Запуск сервисов
docker-compose up -d

# Ожидание запуска
sleep 10

# Инициализация базы данных
docker-compose exec backend python init_db.py

# Проверка статуса
docker-compose ps
```

## 📊 Проверка развертывания

### Проверка сервисов:
```bash
# Статус контейнеров
docker-compose ps

# Логи сервисов
docker-compose logs -f

# Проверка API
curl http://localhost:8000/docs
```

### Проверка доступности:
- Frontend: http://89.40.233.33:3000
- Backend API: http://89.40.233.33:8000
- API Docs: http://89.40.233.33:8000/docs

## 🔍 Отладка проблем

### Проблемы с базой данных:
```bash
docker-compose exec backend python init_db.py
```

### Проблемы с frontend:
```bash
docker-compose build frontend --no-cache
docker-compose up -d frontend
```

### Проблемы с backend:
```bash
docker-compose build backend --no-cache
docker-compose up -d backend
```

### Просмотр логов:
```bash
# Все сервисы
docker-compose logs -f

# Конкретный сервис
docker-compose logs -f frontend
docker-compose logs -f backend
```

## 🛡️ Безопасность

### Настройка Nginx (рекомендуется):
```nginx
server {
    listen 80;
    server_name mcp-kv.ru www.mcp-kv.ru;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Настройка SSL (Let's Encrypt):
```bash
# Установка certbot
apt install certbot python3-certbot-nginx

# Получение сертификата
certbot --nginx -d mcp-kv.ru -d www.mcp-kv.ru
```

## 📈 Мониторинг

### Проверка ресурсов:
```bash
# Использование ресурсов
docker stats

# Место на диске
df -h

# Процессы
htop
```

### Автоматический перезапуск:
```bash
# Добавление в crontab для автоматического перезапуска
crontab -e

# Добавить строку (перезапуск каждый день в 3:00):
0 3 * * * cd /root/sofiya && docker-compose restart
```

## 🎯 Готово!

После успешного развертывания у вас будет:
- ✅ Полнофункциональная WordPress MCP Platform
- ✅ Панель управления с инструментами
- ✅ Настройки подключений
- ✅ API для интеграции с ChatGPT
- ✅ Безопасная аутентификация
- ✅ Современный UI/UX

**Доступ к платформе:** http://89.40.233.33:3000

