# 🚀 Обновление до версии 3.0.0

**Текущая версия:** 2.0.0 → **Новая версия:** 3.0.0

**Дата релиза:** 15 октября 2025 г.

---

## 📋 Что нового в v3.0.0

✅ **Все 5 методов Wordstat API полностью работают!**
- `wordstat_get_user_info` ✓
- `wordstat_get_regions_tree` ✓ (ИСПРАВЛЕН)
- `wordstat_get_top_requests` ✓
- `wordstat_get_regions` ✓ (ИСПРАВЛЕН)
- `wordstat_get_dynamics` ✓

🐛 **Исправлены все критические баги**
🔧 **Улучшено логирование и обработка ошибок**
📝 **Добавлена полная документация**

---

## ⚡ БЫСТРОЕ ОБНОВЛЕНИЕ (1 команда)

### На сервере:

```bash
cd /opt/sofiya/backend && git fetch --tags && git checkout v3.0.0 && sudo systemctl restart sofa-backend && sudo systemctl status sofa-backend --no-pager
```

---

## 📝 ПОШАГОВОЕ ОБНОВЛЕНИЕ

### Шаг 1: Подключение к серверу

```bash
ssh root@your-server.com
```

### Шаг 2: Переход в директорию проекта

```bash
cd /opt/sofiya/backend
```

### Шаг 3: Резервное копирование (опционально, но рекомендуется)

```bash
# Резервная копия базы данных
cp app.db app.db.backup-$(date +%Y%m%d-%H%M%S)

# Резервная копия конфигурации
cp .env .env.backup-$(date +%Y%m%d-%H%M%S)
```

### Шаг 4: Получение обновления

```bash
# Получить все теги
git fetch --tags

# Переключиться на v3.0.0
git checkout v3.0.0
```

### Шаг 5: Обновление зависимостей (если требуется)

```bash
# Активировать виртуальное окружение (если используется)
source venv/bin/activate

# Обновить зависимости
pip install -r requirements.txt --upgrade
```

### Шаг 6: Проверка базы данных

```bash
# База данных автоматически обновится при первом запуске
# Столбец wordstat_token_expires будет добавлен автоматически
```

### Шаг 7: Перезапуск backend

```bash
sudo systemctl restart sofa-backend
```

### Шаг 8: Проверка статуса

```bash
sudo systemctl status sofa-backend
```

### Шаг 9: Проверка логов

```bash
sudo journalctl -u sofa-backend -n 50 --no-pager
```

---

## 🔍 ПРОВЕРКА ПОСЛЕ ОБНОВЛЕНИЯ

### 1. Проверка версии

```bash
git describe --tags
# Должно вывести: v3.0.0
```

### 2. Проверка работы backend

```bash
curl http://localhost:8000/health
# Ожидается: {"status": "ok"}
```

### 3. Проверка логов на ошибки

```bash
sudo journalctl -u sofa-backend -n 100 | grep -i error
# Не должно быть критических ошибок
```

### 4. Тестирование в ChatGPT

Протестируйте все 5 методов Wordstat:

```
1. wordstat_get_user_info
   → Должен показать логин, лимиты и квоты

2. wordstat_get_regions_tree
   → Должен вернуть дерево регионов Yandex

3. wordstat_get_top_requests
   Параметры: phrase: "купить носки", numPhrases: 10
   → Должен вернуть топ-10 запросов

4. wordstat_get_regions
   Параметры: phrase: "купить носки", devices: ["desktop"]
   → Должен вернуть распределение по регионам

5. wordstat_get_dynamics
   Параметры: phrase: "купить носки", period: "monthly", fromDate: "2024-01-01"
   → Должен вернуть месячную динамику
```

---

## 🔧 ОБНОВЛЕНИЕ FRONTEND (опционально)

Если вы также хотите обновить frontend:

```bash
cd /opt/sofiya/frontend

# Получить изменения
git pull origin main

# Установить зависимости
npm install

# Собрать проект
npm run build

# Перезапустить frontend
pm2 restart frontend

# Проверить статус
pm2 status
```

---

## 🐛 РЕШЕНИЕ ПРОБЛЕМ

### Проблема: Backend не запускается

**Решение:**
```bash
# Проверить логи
sudo journalctl -u sofa-backend -n 100

# Убедиться, что порт 8000 свободен
sudo lsof -i :8000

# Перезапустить принудительно
sudo systemctl stop sofa-backend
sudo systemctl start sofa-backend
```

### Проблема: Ошибка "column wordstat_token_expires not found"

**Решение:**
```bash
# Выполнить миграцию вручную
cd /opt/sofiya/backend

# Создать скрипт миграции
cat > migrate_db.py << 'EOF'
import sqlite3

conn = sqlite3.connect('app.db')
cursor = conn.cursor()

try:
    cursor.execute('ALTER TABLE user_settings ADD COLUMN wordstat_token_expires DATETIME')
    conn.commit()
    print("✅ Столбец wordstat_token_expires добавлен")
except sqlite3.OperationalError as e:
    if 'duplicate column name' in str(e):
        print("✅ Столбец уже существует")
    else:
        print(f"❌ Ошибка: {e}")

conn.close()
EOF

# Запустить миграцию
python migrate_db.py

# Перезапустить backend
sudo systemctl restart sofa-backend
```

### Проблема: Wordstat API возвращает ошибки

**Проверка:**
```bash
# Проверить токен в базе
cd /opt/sofiya/backend
sqlite3 app.db "SELECT email, wordstat_access_token IS NOT NULL as has_token FROM user_settings;"

# Если токена нет, нужно переавторизоваться в UI
```

### Проблема: Frontend не обновляется

**Решение:**
```bash
cd /opt/sofiya/frontend

# Очистить кэш
rm -rf .next
rm -rf node_modules

# Переустановить зависимости
npm install

# Пересобрать
npm run build

# Перезапустить
pm2 restart frontend
pm2 logs frontend --lines 50
```

---

## ↩️ ОТКАТ К ПРЕДЫДУЩЕЙ ВЕРСИИ

Если что-то пошло не так:

```bash
cd /opt/sofiya/backend

# Вернуться к v2.0.0
git checkout v2.0.0

# Восстановить базу данных (если делали backup)
cp app.db.backup-YYYYMMDD-HHMMSS app.db

# Перезапустить
sudo systemctl restart sofa-backend

# Проверить
sudo systemctl status sofa-backend
```

---

## 📊 ИЗМЕНЕНИЯ В API

### Новые параметры:

**wordstat_get_top_requests:**
- `devices` теперь принимает: `all`, `desktop`, `phone`, `tablet`
- ❌ `mobile` больше не работает → используйте `phone` или `tablet`

**wordstat_get_regions:**
- Добавлен параметр `regionType`: `all`, `cities`, `regions`
- Параметр `devices` обновлен (см. выше)

**wordstat_get_dynamics:**
- `fromDate` (обязательный) - дата в формате YYYY-MM-DD
- `toDate` (опциональный) - дата в формате YYYY-MM-DD
- `period`: `monthly`, `weekly`, `daily`

### Изменения в форматах ответов:

**wordstat_get_regions_tree:**
- API возвращает список с полями `value` и `label`
- `children` может быть `null` (не только пустой массив)

**wordstat_get_regions:**
- Использует поля: `regionId`, `count`, `share`, `affinityIndex`

---

## 📚 ДОПОЛНИТЕЛЬНАЯ ДОКУМЕНТАЦИЯ

После обновления ознакомьтесь с:
- `WORDSTAT_API_STATUS.md` - полная документация по Wordstat API
- `RELEASE_v3.0.0.md` - детальное описание релиза
- `CHANGELOG.md` - история всех изменений
- `UPDATE_COMMANDS.txt` - шпаргалка по командам

---

## ✅ ЧЕКЛИСТ ОБНОВЛЕНИЯ

- [ ] Резервная копия БД создана
- [ ] Backend обновлен до v3.0.0
- [ ] Backend перезапущен успешно
- [ ] Логи проверены (нет критических ошибок)
- [ ] Все 5 методов Wordstat протестированы
- [ ] Frontend обновлен (опционально)
- [ ] Документация прочитана

---

## 🆘 ПОДДЕРЖКА

Если возникли проблемы:

1. 📧 Email: support@mcp-kv.ru
2. 💬 Telegram: https://t.me/maya_pro
3. 🐛 GitHub Issues: https://github.com/Horosheff/sofa/issues
4. 📝 Документация: https://github.com/Horosheff/sofa/blob/main/WORDSTAT_API_STATUS.md

---

**🎉 Поздравляем с обновлением до v3.0.0!**

Теперь у вас полностью рабочая интеграция с Yandex Wordstat API! 🚀

