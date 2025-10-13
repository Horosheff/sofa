# 🐳 Docker Развертывание WordPress MCP Platform

## 🚀 Быстрый старт

### 1. Клонирование репозитория
```bash
git clone https://github.com/Horosheff/sofiya.git
cd sofiya
```

### 2. Настройка окружения
```bash
# Скопируйте и отредактируйте production переменные
cp env.production .env

# Отредактируйте .env файл с вашими настройками
nano .env
```

### 3. Развертывание
```bash
# Сделайте скрипт исполняемым
chmod +x deploy.sh

# Запустите развертывание
./deploy.sh
```

## 🔧 Ручное развертывание

### Сборка и запуск
```bash
# Сборка образов
docker-compose build

# Запуск сервисов
docker-compose up -d

# Проверка статуса
docker-compose ps
```

### Остановка сервисов
```bash
docker-compose down
```

## 📊 Мониторинг

### Просмотр логов
```bash
# Все сервисы
docker-compose logs -f

# Конкретный сервис
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Проверка статуса
```bash
docker-compose ps
```

## 🌐 Доступные сервисы

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Redis**: localhost:6379

## 🔒 Production настройки

### SSL сертификаты
1. Поместите SSL сертификаты в папку `ssl/`:
   - `ssl/cert.pem` - сертификат
   - `ssl/key.pem` - приватный ключ

### Environment переменные
Обязательно измените в `.env`:
- `SECRET_KEY` - секретный ключ для JWT
- `ALLOWED_ORIGINS` - разрешенные домены
- `NGINX_HOST` - ваш домен

## 🛠 Устранение неполадок

### Проблемы с портами
```bash
# Проверьте занятые порты
netstat -tulpn | grep :3000
netstat -tulpn | grep :8000

# Остановите конфликтующие сервисы
sudo systemctl stop nginx  # если nginx запущен
```

### Проблемы с Docker
```bash
# Очистка Docker
docker system prune -a

# Пересборка образов
docker-compose build --no-cache
```

### Проблемы с базой данных
```bash
# Пересоздание базы данных
docker-compose down -v
docker-compose up -d
```

## 📁 Структура проекта

```
sofiya/
├── backend/
│   ├── Dockerfile
│   ├── .dockerignore
│   └── ...
├── frontend/
│   ├── Dockerfile
│   ├── .dockerignore
│   └── ...
├── docker-compose.yml
├── nginx.conf
├── deploy.sh
├── env.production
└── DOCKER_README.md
```

## 🔄 Обновление

```bash
# Получение обновлений
git pull origin main

# Пересборка и перезапуск
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## 📞 Поддержка

При возникновении проблем:
1. Проверьте логи: `docker-compose logs -f`
2. Проверьте статус: `docker-compose ps`
3. Перезапустите сервисы: `docker-compose restart`
