# 🚀 Запуск Frontend на сервере

## 📋 Быстрый старт (Production)

### Способ 1: PM2 (рекомендуется)

```bash
ssh your-server
cd /var/www/sofiya/frontend

# 1. Собрать production сборку
npm run build

# 2. Запустить через PM2
pm2 start npm --name "frontend" -- start

# ИЛИ запустить на порту 3000
pm2 start npm --name "frontend" -- start -- -p 3000

# 3. Сохранить конфигурацию
pm2 save

# 4. Включить автозапуск
pm2 startup
```

---

## 🔧 Способ 2: С использованием ecosystem.config.js

### Создайте файл `frontend/ecosystem.config.js`:

```javascript
module.exports = {
  apps: [{
    name: 'sofiya-frontend',
    script: 'npm',
    args: 'start',
    cwd: '/var/www/sofiya/frontend',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '500M',
    env: {
      NODE_ENV: 'production',
      PORT: 3000
    },
    error_file: '/var/www/sofiya/logs/frontend-error.log',
    out_file: '/var/www/sofiya/logs/frontend-out.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
  }]
}
```

### Запуск:

```bash
cd /var/www/sofiya/frontend

# Собрать
npm run build

# Запустить
pm2 start ecosystem.config.js

# Сохранить
pm2 save
```

---

## 🌐 Способ 3: Через Nginx (reverse proxy)

### 1. Запустите frontend на localhost:3000

```bash
cd /var/www/sofiya/frontend
npm run build
pm2 start npm --name "frontend" -- start
```

### 2. Настройте Nginx

Создайте файл `/etc/nginx/sites-available/sofiya-frontend`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Frontend (Next.js)
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # MCP SSE
    location /mcp/ {
        proxy_pass http://localhost:8000/mcp/;
        proxy_http_version 1.1;
        proxy_set_header Connection '';
        proxy_buffering off;
        proxy_cache off;
        chunked_transfer_encoding off;
    }
}
```

### 3. Активируйте конфигурацию

```bash
sudo ln -s /etc/nginx/sites-available/sofiya-frontend /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## 📦 Полная установка с нуля

```bash
# 1. Перейти в директорию
cd /var/www/sofiya/frontend

# 2. Установить зависимости (если нужно)
npm install

# 3. Создать .env.local (если нужно)
cat > .env.local << EOF
NEXT_PUBLIC_API_URL=https://your-domain.com/api
EOF

# 4. Собрать production сборку
npm run build

# 5. Проверить сборку
ls -la .next/

# 6. Запустить через PM2
pm2 start npm --name "sofiya-frontend" -- start

# 7. Проверить статус
pm2 list

# 8. Посмотреть логи
pm2 logs sofiya-frontend

# 9. Сохранить конфигурацию
pm2 save

# 10. Настроить автозапуск
pm2 startup
```

---

## 🔍 Проверка работы

```bash
# 1. Проверить процесс PM2
pm2 list

# 2. Проверить логи
pm2 logs frontend --lines 50

# 3. Проверить порт
netstat -tulpn | grep :3000
# ИЛИ
ss -tulpn | grep :3000

# 4. Проверить HTTP
curl http://localhost:3000

# 5. Проверить через браузер
# Открыть: http://your-server-ip:3000
```

---

## 🛠️ Управление процессом

```bash
# Запуск
pm2 start frontend

# Остановка
pm2 stop frontend

# Перезапуск
pm2 restart frontend

# Удаление
pm2 delete frontend

# Логи в реальном времени
pm2 logs frontend

# Мониторинг
pm2 monit
```

---

## 🔄 Обновление после изменений

```bash
cd /var/www/sofiya/frontend

# 1. Остановить
pm2 stop frontend

# 2. Обновить код
git pull origin main

# 3. Установить зависимости (если изменились)
npm install

# 4. Пересобрать
npm run build

# 5. Перезапустить
pm2 restart frontend

# 6. Проверить логи
pm2 logs frontend --lines 50
```

---

## ⚠️ Решение проблем

### Проблема: "Port 3000 already in use"

```bash
# Найти процесс на порту 3000
lsof -i :3000
# ИЛИ
fuser -k 3000/tcp

# Остановить все PM2 процессы
pm2 stop all
pm2 delete all

# Запустить заново
pm2 start npm --name "frontend" -- start
```

### Проблема: "Module not found"

```bash
cd /var/www/sofiya/frontend
rm -rf node_modules package-lock.json
npm install
npm run build
pm2 restart frontend
```

### Проблема: "Memory exceeded"

```bash
# Увеличить лимит памяти
pm2 delete frontend
pm2 start npm --name "frontend" --max-memory-restart 1000M -- start
```

### Проблема: Логи показывают ошибки

```bash
# Посмотреть полные логи
pm2 logs frontend --lines 200

# Посмотреть логи ошибок
pm2 logs frontend --err

# Очистить логи
pm2 flush
```

---

## 📊 Мониторинг

```bash
# Статус всех процессов
pm2 status

# Детальная информация
pm2 show frontend

# Использование ресурсов
pm2 monit

# Статистика
pm2 describe frontend
```

---

## 🔐 Переменные окружения

Создайте файл `/var/www/sofiya/frontend/.env.production`:

```bash
# API URL
NEXT_PUBLIC_API_URL=https://your-domain.com

# Другие переменные
NEXT_PUBLIC_SITE_URL=https://your-domain.com
NODE_ENV=production
```

---

## ✅ Чек-лист после запуска

- [ ] Frontend собран: `ls -la .next/`
- [ ] PM2 процесс работает: `pm2 list`
- [ ] Порт открыт: `netstat -tulpn | grep 3000`
- [ ] HTTP отвечает: `curl http://localhost:3000`
- [ ] Логи без ошибок: `pm2 logs frontend`
- [ ] Nginx настроен (если используется)
- [ ] Автозапуск включен: `pm2 startup`
- [ ] Конфигурация сохранена: `pm2 save`

---

## 📝 Полный скрипт запуска

Создайте файл `/var/www/sofiya/start-frontend.sh`:

```bash
#!/bin/bash

echo "Starting Sofiya Frontend..."

cd /var/www/sofiya/frontend

# Проверка зависимостей
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Сборка
echo "Building production..."
npm run build

# Остановка старого процесса
pm2 stop frontend 2>/dev/null || true
pm2 delete frontend 2>/dev/null || true

# Запуск нового
echo "Starting PM2 process..."
pm2 start npm --name "frontend" -- start

# Сохранение
pm2 save

echo "Frontend started successfully!"
echo "Check status: pm2 list"
echo "View logs: pm2 logs frontend"
```

Сделать исполняемым:

```bash
chmod +x /var/www/sofiya/start-frontend.sh
```

Запустить:

```bash
/var/www/sofiya/start-frontend.sh
```

---

## 🌐 Доступ

После запуска frontend будет доступен:

- **Локально:** http://localhost:3000
- **По IP:** http://your-server-ip:3000
- **Через домен:** https://your-domain.com (если Nginx настроен)

---

**Готово!** Frontend запущен и работает! 🚀

