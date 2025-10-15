# 🚀 ПРИМЕНЕНИЕ ОБНОВЛЕНИЯ v4.2 НА СЕРВЕРЕ

**Дата:** 15 октября 2025  
**Версия:** 4.2  
**Время выполнения:** ~2 минуты

---

## 🎯 ЧТО ДЕЛАЕТ ЭТО ОБНОВЛЕНИЕ

- ✅ Добавляет 5 инструментов для управления Pages в WordPress
- ✅ Удаляет 4 инструмента Users (не нужны для основной работы)
- ✅ Удаляет 2 служебных инструмента Wordstat (автоматизированы)
- ✅ Итого: 33 инструмента (было 34)

---

## ⚡ БЫСТРОЕ ПРИМЕНЕНИЕ (СКОПИРУЙ И ВСТАВЬ)

### 1️⃣ Подключиться к серверу
```bash
ssh root@89.40.233.33
# или
ssh your-server
```

### 2️⃣ Применить обновление (ВСЁ СРАЗУ)
```bash
cd /opt/sofiya && \
git pull origin main && \
pm2 restart backend && \
echo "✅ ОБНОВЛЕНИЕ ПРИМЕНЕНО!" && \
pm2 logs backend --lines 20
```

---

## 📋 ПОШАГОВАЯ ИНСТРУКЦИЯ (ДЕТАЛЬНО)

### Шаг 1: Перейти в директорию проекта
```bash
cd /opt/sofiya
```

### Шаг 2: Проверить текущую версию (опционально)
```bash
git log --oneline -1
```

### Шаг 3: Получить изменения с GitHub
```bash
git pull origin main
```

**Ожидаемый вывод:**
```
remote: Enumerating objects: 8, done.
remote: Counting objects: 100% (8/8), done.
Updating abc1234..def5678
Fast-forward
 backend/app/mcp_handlers.py  | 120 ++++++++++---------
 backend/app/wordpress_tools.py | 28 ++---
 backend/test_modules.py       | 8 +-
 CHANGELOG_v4.2.md             | 1 +
 4 files changed, 89 insertions(+), 68 deletions(-)
```

### Шаг 4: Перезапустить backend
```bash
pm2 restart backend
```

**Ожидаемый вывод:**
```
[PM2] Applying action restartProcessId on app [backend](ids: [ 0 ])
[PM2] [backend](0) ✓
```

### Шаг 5: Проверить логи
```bash
pm2 logs backend --lines 30
```

**В логах должно быть:**
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

## ✅ ПРОВЕРКА ОБНОВЛЕНИЯ

### 1. Проверить статус PM2
```bash
pm2 list
```

**Ожидаемый результат:**
```
┌────┬────────────┬──────────┬──────┬───────────┬──────────┐
│ id │ name       │ mode     │ ↺    │ status    │ cpu      │
├────┼────────────┼──────────┼──────┼───────────┼──────────┤
│ 0  │ backend    │ fork     │ 5    │ online    │ 0%       │
│ 2  │ frontend   │ fork     │ 0    │ online    │ 0%       │
└────┴────────────┴──────────┴──────┴───────────┴──────────┘
```

### 2. Проверить количество инструментов
```bash
curl -s http://localhost:8000/mcp/tools | python3 -c "import sys, json; print(len(json.load(sys.stdin)))"
```

**Ожидаемый результат:** `33`

### 3. Проверить Pages инструменты
```bash
curl -s http://localhost:8000/mcp/tools | grep -o "wordpress_.*_page" | sort -u
```

**Ожидаемый результат:**
```
wordpress_create_page
wordpress_delete_page
wordpress_get_pages
wordpress_search_pages
wordpress_update_page
```

### 4. Убедиться, что Users удалены
```bash
curl -s http://localhost:8000/mcp/tools | grep -o "wordpress_.*_user"
```

**Ожидаемый результат:** (пусто - инструменты удалены)

### 5. Проверить Wordstat
```bash
curl -s http://localhost:8000/mcp/tools | grep -o "wordstat_.*" | sort -u
```

**Ожидаемый результат:**
```
wordstat_get_dynamics
wordstat_get_regions
wordstat_get_regions_tree
wordstat_get_top_requests
wordstat_get_user_info
```

(5 инструментов, без `wordstat_set_token` и `wordstat_auto_setup`)

---

## 🔧 РЕШЕНИЕ ПРОБЛЕМ

### Проблема 1: `git pull` не работает

**Симптом:**
```
error: Your local changes to the following files would be overwritten by merge
```

**Решение:**
```bash
# Сохранить текущие изменения
git stash

# Применить обновление
git pull origin main

# Вернуть изменения (если нужно)
git stash pop
```

### Проблема 2: Backend не запускается

**Решение:**
```bash
# Остановить все процессы
pm2 stop backend

# Проверить логи ошибок
pm2 logs backend --err --lines 50

# Запустить заново
pm2 start backend

# Если не помогло - перезапустить PM2
pm2 kill
cd /opt/sofiya/backend
pm2 start --name backend python3 -- -m uvicorn app.main:app --host 0.0.0.0 --port 8000
pm2 save
```

### Проблема 3: Инструментов не 33

**Диагностика:**
```bash
# Проверить версию кода
cd /opt/sofiya
git log --oneline -1

# Проверить, что изменения применились
cat backend/app/mcp_handlers.py | grep -A5 "def get_wordpress_tools"

# Перезагрузить Python modules
pm2 restart backend --update-env
```

---

## 📊 ЧТО ИЗМЕНИЛОСЬ (ТЕХНИЧЕСКИ)

### Файлы:
1. `backend/app/mcp_handlers.py` - определения инструментов MCP
2. `backend/app/wordpress_tools.py` - обработчики WordPress инструментов
3. `backend/test_modules.py` - обновлены тесты
4. `CHANGELOG_v4.2.md` - описание изменений

### Инструменты:
| Категория | До v4.2 | После v4.2 | Изменение |
|-----------|---------|------------|-----------|
| WordPress Posts | 6 | 6 | - |
| WordPress Categories | 4 | 4 | - |
| WordPress Tags | 4 | 4 | - |
| WordPress Pages | 0 | 5 | +5 ✅ |
| WordPress Media | 4 | 4 | - |
| WordPress Comments | 5 | 5 | - |
| WordPress Users | 4 | 0 | -4 ❌ |
| **WordPress ИТОГО** | **27** | **28** | **+1** |
| Wordstat API | 7 | 5 | -2 ❌ |
| **ВСЕГО** | **34** | **33** | **-1** |

---

## 🎉 ГОТОВО!

После успешного применения обновления:
1. ✅ В дашборде будет 33 инструмента
2. ✅ Появятся инструменты для Pages
3. ✅ Исчезнут Users и служебные Wordstat инструменты
4. ✅ Всё работает стабильно

---

## 📞 ПОДДЕРЖКА

Если что-то пошло не так:
1. Проверь логи: `pm2 logs backend --lines 100`
2. Проверь статус: `pm2 list`
3. Перезапусти: `pm2 restart backend`
4. Напиши в Issues: https://github.com/Horosheff/sofa/issues

---

**Успешного обновления! 🚀**

