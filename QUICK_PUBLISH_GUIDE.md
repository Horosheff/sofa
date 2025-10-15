# 🚀 Быстрая публикация v4.0.0

## Шаг 1: Подготовка (локально)

```bash
# Проверьте статус
git status

# Запустите скрипт публикации (или выполните команды вручную)
bash PUBLISH_V4.sh
```

## Шаг 2: Коммит и пуш

```bash
# Коммит
git commit -m "v4.0.0: Modular architecture refactoring

BREAKING CHANGES:
- Backend разбит на модули: helpers, mcp_handlers, wordpress_tools, wordstat_tools
- Добавлена админ панель для управления платформой
- Улучшена безопасность: validation, sanitization, rate limiting

NEW:
- helpers.py: 15+ utility functions
- mcp_handlers.py: SSE Manager, OAuth Store, MCP tools
- wordpress_tools.py: 18 WordPress instruments
- wordstat_tools.py: 7 Wordstat instruments
- admin_routes.py: Admin API endpoints
- Admin panel: user management, logs, statistics

IMPROVED:
- main.py: -443 lines (-19% code)
- Security: URL/email validation, XSS protection
- Monitoring: API metrics, sensitive data masking
- Testing: 37 automated tests

DOCS:
- RELEASE_NOTES_v4.md: Full changelog
- DEPLOY_v4.md: Deployment guide
- TEST_REPORT.md: Test results"

# Создайте тег
git tag -a v4.0.0 -m "Version 4.0.0 - Modular Architecture"

# Пуш на GitHub
git push origin main
git push origin v4.0.0
```

## Шаг 3: Деплой на сервер

```bash
# SSH на сервер
ssh root@mcp-kv.ru

# Перейдите в проект
cd /var/www/sofa

# Обновите код
git pull origin main

# Проверьте новые модули
cd backend
source venv/bin/activate
python test_modules.py

# Если тесты прошли, рестартуйте backend
pm2 restart mcp-backend

# Соберите и рестартуйте frontend
cd ../frontend
npm run build
pm2 restart mcp-frontend

# Проверьте статус
pm2 status
pm2 logs mcp-backend --lines 50
```

## Шаг 4: Проверка

1. Откройте https://mcp-kv.ru
2. Войдите в систему
3. Проверьте, что 25 инструментов видны
4. Откройте настройки - проверьте WordPress инструкцию
5. Проверьте статистику
6. (Опционально) Войдите как админ на https://mcp-kv.ru/admin

## ✅ Готово!

Версия 4.0.0 опубликована и работает на production!

---

## Откат (если что-то пошло не так)

```bash
# На сервере
cd /var/www/sofa
git checkout v3.0.0  # или последний рабочий коммит
pm2 restart all
```

