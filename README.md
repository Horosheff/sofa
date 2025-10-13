# WordPress MCP Platform

Полнофункциональная платформа для управления WordPress через MCP (Model Context Protocol) с интеграцией Wordstat и Google сервисов.

## 🚀 Возможности

### 📝 WordPress управление
- Создание, обновление, удаление постов
- Управление категориями и медиафайлами
- Массовые операции с контентом
- Поиск и фильтрация контента

### 📊 Wordstat аналитика
- Получение трендов поисковых запросов
- Анализ региональной статистики
- Топ запросы по ключевым словам
- Динамика популярности запросов

### 🔍 Google MCP интеграция
- Google Trends анализ
- Объем поисковых запросов
- Анализ ключевых слов
- YouTube аналитика

### ⚙️ Настройки и подключения
- Настройка WordPress подключений
- Конфигурация Wordstat API
- MCP SSE сервер для ChatGPT
- Персонализация интерфейса

## 🛠️ Технологии

- **Frontend**: Next.js 15, React, TypeScript, Tailwind CSS
- **Backend**: FastAPI, Python 3.11, SQLAlchemy
- **База данных**: SQLite (с возможностью миграции на PostgreSQL)
- **Кэширование**: Redis
- **Контейнеризация**: Docker, Docker Compose
- **Аутентификация**: JWT токены
- **Состояние**: Zustand с localStorage

## 📦 Установка и запуск

### Локальная разработка

```bash
# Клонирование репозитория
git clone <repository-url>
cd sofiya

# Установка зависимостей
cd frontend && npm install
cd ../backend && pip install -r requirements.txt

# Запуск в режиме разработки
cd frontend && npm run dev
cd ../backend && python -m uvicorn app.main:app --reload
```

### Docker развертывание

```bash
# Клонирование и переход в директорию
git clone <repository-url>
cd sofiya

# Запуск всех сервисов
docker-compose up -d

# Инициализация базы данных
docker-compose exec backend python init_db.py
```

### Продакшен развертывание

```bash
# Использование скрипта развертывания
chmod +x deploy.sh
./deploy.sh
```

## 🔧 Конфигурация

### Переменные окружения

Создайте файл `.env` в корне проекта:

```env
# Database
DATABASE_URL=sqlite:///./app.db

# Security
SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440

# CORS
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com

# Redis
REDIS_URL=redis://redis:6379

# MCP Server
MCP_SERVER_URL=https://your-mcp-server.com
```

### Nginx конфигурация

```nginx
server {
    listen 80;
    server_name yourdomain.com;

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

## 📱 Использование

### 1. Регистрация и вход
- Перейдите на главную страницу
- Зарегистрируйтесь с сильным паролем
- Войдите в систему

### 2. Настройка подключений
- Перейдите в раздел "⚙️ Настройки"
- Настройте WordPress подключение
- Добавьте Wordstat API ключи
- Скопируйте MCP SSE URL для ChatGPT

### 3. Использование инструментов
- Перейдите в раздел "🛠️ Инструменты"
- Выберите нужный инструмент
- Заполните параметры
- Нажмите "🚀 Выполнить"

### 4. Подключение к ChatGPT
- Скопируйте MCP SSE URL из настроек
- В ChatGPT выберите "Connect to MCP Server"
- Вставьте URL и подключитесь
- Используйте инструменты через ChatGPT

## 🔐 Безопасность

- JWT токены для аутентификации
- Валидация паролей (минимум 8 символов, заглавные/строчные буквы, цифры)
- CORS настройки для защиты от CSRF
- Безопасное хранение настроек в базе данных
- HTTPS поддержка для продакшена

## 📊 Мониторинг

```bash
# Проверка статуса сервисов
docker-compose ps

# Просмотр логов
docker-compose logs -f

# Мониторинг ресурсов
docker stats
```

## 🐛 Отладка

### Проблемы с базой данных
```bash
# Пересоздание базы данных
docker-compose exec backend python init_db.py
```

### Проблемы с frontend
```bash
# Пересборка frontend
docker-compose build frontend --no-cache
```

### Проблемы с API
```bash
# Проверка API
curl http://localhost:8000/docs
```

## 📈 Производительность

- Redis кэширование для быстрого доступа
- Оптимизированные SQL запросы
- Lazy loading компонентов
- Минификация и сжатие ресурсов

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для новой функции
3. Внесите изменения
4. Создайте Pull Request

## 📄 Лицензия

MIT License - см. файл LICENSE для деталей.

## 🆘 Поддержка

- 📧 Email: support@example.com
- 💬 Telegram: @your_username
- 🐛 Issues: GitHub Issues

---

**WordPress MCP Platform** - Управляйте WordPress через AI с легкостью! 🚀