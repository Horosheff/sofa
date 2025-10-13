# 🚀 Развертывание на сервере 89.40.233.33

## 📦 Готовые файлы для передачи

### Основные файлы проекта:
- ✅ `docker-compose.yml` - конфигурация Docker
- ✅ `deploy.sh` - скрипт полного развертывания  
- ✅ `quick-deploy.sh` - скрипт быстрого обновления
- ✅ `README.md` - документация проекта
- ✅ `DEPLOYMENT.md` - руководство по развертыванию

### Frontend (Next.js):
- ✅ `frontend/Dockerfile` - образ frontend
- ✅ `frontend/next.config.js` - конфигурация Next.js
- ✅ `frontend/app/` - страницы приложения
- ✅ `frontend/components/` - React компоненты
- ✅ `frontend/store/` - Zustand store
- ✅ `frontend/package.json` - зависимости

### Backend (FastAPI):
- ✅ `backend/Dockerfile` - образ backend
- ✅ `backend/init_db.py` - инициализация БД
- ✅ `backend/app/` - API приложение
- ✅ `backend/requirements.txt` - Python зависимости

## 🚀 Команды для развертывания

### 1. Передача файлов на сервер:

```bash
# Создание архива (исключая ненужные файлы)
tar -czf sofiya-update.tar.gz \
    --exclude=node_modules \
    --exclude=.git \
    --exclude=*.db \
    --exclude=.next \
    --exclude=__pycache__ \
    --exclude=*.pyc \
    frontend/ \
    backend/ \
    docker-compose.yml \
    deploy.sh \
    quick-deploy.sh \
    README.md \
    DEPLOYMENT.md

# Передача на сервер
scp sofiya-update.tar.gz root@89.40.233.33:/tmp/
```

### 2. Развертывание на сервере:

```bash
# Подключение к серверу
ssh root@89.40.233.33

# Распаковка архива
cd /root
tar -xzf /tmp/sofiya-update.tar.gz

# Переход в директорию проекта
cd sofiya

# Установка прав доступа
chmod +x deploy.sh quick-deploy.sh

# Полное развертывание
./deploy.sh
```

### 3. Проверка развертывания:

```bash
# Статус сервисов
docker-compose ps

# Логи
docker-compose logs -f

# Проверка доступности
curl http://localhost:3000
curl http://localhost:8000/docs
```

## 🔧 Альтернативный способ (если скрипты не работают)

### Ручное развертывание:

```bash
# 1. Остановка существующих контейнеров
docker-compose down

# 2. Очистка старых образов
docker system prune -f

# 3. Сборка новых образов
docker-compose build --no-cache

# 4. Запуск сервисов
docker-compose up -d

# 5. Ожидание запуска
sleep 10

# 6. Инициализация базы данных
docker-compose exec backend python init_db.py

# 7. Проверка статуса
docker-compose ps
```

## 📊 Проверка работоспособности

### Frontend:
- URL: http://89.40.233.33:3000
- Должна загружаться главная страница с формами входа/регистрации

### Backend API:
- URL: http://89.40.233.33:8000/docs
- Должна загружаться документация API

### База данных:
```bash
# Проверка таблиц
docker-compose exec backend python -c "
from app.database import engine
from sqlalchemy import text
with engine.connect() as conn:
    result = conn.execute(text('SELECT name FROM sqlite_master WHERE type=\"table\"'))
    print('Таблицы:', [row[0] for row in result.fetchall()])
"
```

## 🛠️ Настройка Nginx (опционально)

### Создание конфигурации Nginx:

```bash
# Создание конфигурации
cat > /etc/nginx/sites-available/sofiya << 'EOF'
server {
    listen 80;
    server_name mcp-kv.ru www.mcp-kv.ru 89.40.233.33;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /docs {
        proxy_pass http://localhost:8000/docs;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /openapi.json {
        proxy_pass http://localhost:8000/openapi.json;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Активация конфигурации
ln -sf /etc/nginx/sites-available/sofiya /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

## 🎯 Готово!

После успешного развертывания:

- ✅ **Frontend**: http://89.40.233.33:3000
- ✅ **Backend API**: http://89.40.233.33:8000
- ✅ **API Docs**: http://89.40.233.33:8000/docs
- ✅ **Домен**: http://mcp-kv.ru (если настроен Nginx)

### Функции платформы:
- 🔐 Регистрация и авторизация
- 🛠️ Панель инструментов WordPress/Wordstat/Google
- ⚙️ Настройки подключений
- 🔗 MCP SSE сервер для ChatGPT
- 📱 Адаптивный дизайн
- 🚀 Современный UI/UX

