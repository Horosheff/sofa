# 🚀 Быстрое развёртывание "ВСЁ ПОДКЛЮЧЕНО"

## 📦 Подготовка к публикации на GitHub

### 1. Проверка изменений
```bash
git status
```

### 2. Добавление файлов
```bash
git add frontend/app/page.tsx
git add frontend/app/globals.css
git add frontend/components/Dashboard.tsx
git add frontend/components/LoginForm.tsx
git add frontend/components/RegisterForm.tsx
git add frontend/components/SettingsPanel.tsx
git add frontend/components/ToolsPanel.tsx
git add frontend/components/PasswordField.tsx
git add frontend/components/ToastContainer.tsx
git add frontend/components/ToastNotification.tsx
git add frontend/hooks/useToast.ts
git add .gitignore
git add README.md
```

### 3. Коммит изменений
```bash
git commit -m "🎨 Version 2.0: Glassmorphism UI + Lava Lamp + Matrix Effect

✨ Новые функции:
- Современный glassmorphism дизайн
- Анимированный фон в стиле лавовой лампы
- Эффект падающей матрицы
- Messenger-style toast уведомления
- Полностью адаптивный дизайн
- Обновлённые формы входа и регистрации
- Упрощённый OAuth flow для Wordstat
- Интеграция с Telegram и VK

🎨 Улучшения дизайна:
- Новая главная страница с крупным заголовком
- Обновлённый header с градиентами
- 3-колоночная сетка для инструментов
- Анимированные статусы подключений
- Тёмная тема с полупрозрачными элементами

🔧 Технические улучшения:
- React hooks для toast notifications
- Framer Motion для анимаций
- CSS переменные для единообразия
- Оптимизация производительности
- Улучшенная мобильная адаптация"
```

### 4. Отправка на GitHub
```bash
git push origin main
```

---

## 🖥️ Развёртывание на сервере

### Быстрый способ (через Git)

```bash
# 1. Подключение к серверу
ssh root@89.40.233.33

# 2. Переход в директорию проекта
cd /root/sofa

# 3. Получение последних изменений
git pull origin main

# 4. Перезапуск frontend
cd frontend
npm install  # если добавлены новые зависимости
npm run build
pm2 restart frontend

# 5. Перезапуск backend (если были изменения)
cd ../backend
source venv/bin/activate
pip install -r requirements.txt  # если добавлены новые зависимости
pm2 restart backend

# 6. Проверка статуса
pm2 status
pm2 logs
```

### Альтернативный способ (через Docker)

```bash
# 1. Подключение к серверу
ssh root@89.40.233.33

# 2. Переход в директорию проекта
cd /root/sofa

# 3. Получение последних изменений
git pull origin main

# 4. Пересборка и перезапуск контейнеров
docker-compose down
docker-compose build
docker-compose up -d

# 5. Проверка логов
docker-compose logs -f
```

---

## 🔍 Проверка развёртывания

### 1. Проверка frontend
```bash
curl -I https://mcp-kv.ru
```

### 2. Проверка backend
```bash
curl https://mcp-kv.ru/api/health
```

### 3. Проверка через браузер
- Откройте https://mcp-kv.ru
- Проверьте эффект матрицы (зелёные падающие символы)
- Проверьте лавовую лампу (анимированные цветные капли)
- Проверьте адаптивность (измените размер окна)
- Попробуйте зарегистрироваться / войти
- Проверьте dashboard и настройки

---

## 🐛 Устранение проблем

### Frontend не запускается
```bash
# Проверка логов
pm2 logs frontend

# Перезапуск
pm2 restart frontend

# Если не помогает - полная пересборка
cd /root/sofa/frontend
npm install
npm run build
pm2 restart frontend
```

### Backend не запускается
```bash
# Проверка логов
pm2 logs backend

# Перезапуск
pm2 restart backend

# Проверка базы данных
cd /root/sofa/backend
python init_db.py
```

### Nginx ошибки
```bash
# Проверка конфигурации
nginx -t

# Перезагрузка
systemctl reload nginx

# Проверка логов
tail -f /var/log/nginx/error.log
```

### CSS/JS не обновляются
```bash
# Очистка кэша Next.js
cd /root/sofa/frontend
rm -rf .next
npm run build
pm2 restart frontend

# Очистка кэша Nginx
systemctl reload nginx
```

---

## 📊 Мониторинг

### PM2
```bash
# Статус всех процессов
pm2 status

# Логи в реальном времени
pm2 logs

# Мониторинг ресурсов
pm2 monit
```

### System
```bash
# Использование диска
df -h

# Использование памяти
free -h

# Процессы
top
```

---

## 🎉 Готово!

Ваше приложение "ВСЁ ПОДКЛЮЧЕНО" развёрнуто и работает!

### Полезные ссылки:
- **Сайт**: https://mcp-kv.ru
- **GitHub**: https://github.com/Horosheff/sofa
- **Telegram**: https://t.me/maya_pro
- **VK**: https://vk.com/kov4eg_ai

