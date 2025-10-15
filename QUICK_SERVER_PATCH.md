# 🚀 Быстрое применение PATCH v4.1 на сервере

## ⚡ Самый быстрый способ (одна команда)

Подключитесь к серверу и выполните:

```bash
ssh your-server
cd /var/www/sofiya && pm2 stop all && git pull origin main && cd backend && python test_modules.py && cd .. && pm2 restart all
```

✅ **Готово!** Патч применен.

---

## 🔧 Автоматическая установка (рекомендуется)

```bash
ssh your-server
cd /var/www/sofiya

# Скачать и запустить скрипт
curl -o APPLY_PATCH_v4.1.sh https://raw.githubusercontent.com/Horosheff/sofa/main/APPLY_PATCH_v4.1.sh
chmod +x APPLY_PATCH_v4.1.sh
./APPLY_PATCH_v4.1.sh
```

Скрипт автоматически:
- ✅ Остановит сервисы
- ✅ Создаст бэкап
- ✅ Применит патч
- ✅ Запустит тесты (должно быть 7/7)
- ✅ Перезапустит сервисы

---

## 📝 Пошаговая установка

```bash
# 1. Подключиться к серверу
ssh your-server

# 2. Перейти в директорию проекта
cd /var/www/sofiya

# 3. Остановить сервисы
pm2 stop all

# 4. Применить патч
git pull origin main

# 5. Запустить тесты
cd backend
python test_modules.py

# Должен вывести:
# ИТОГО: 7/7 тестов пройдено
# ВСЕ ТЕСТЫ ПРОЙДЕНЫ!

# 6. Проверить количество инструментов
python -c "from app.mcp_handlers import get_all_mcp_tools; print(f'Tools: {len(get_all_mcp_tools())}')"

# Должен вывести: Tools: 34

# 7. Перезапустить сервисы
cd ..
pm2 restart all

# 8. Проверить статус
pm2 list
```

---

## ✅ Проверка после установки

```bash
# Проверить логи
pm2 logs --lines 50

# Проверить API
curl -X POST http://localhost:8000/mcp/sse/test \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/list","id":1}'

# Должно вернуть 34 инструмента
```

---

## 📊 Что изменится

| Параметр | До патча | После патча |
|----------|----------|-------------|
| **Рабочих инструментов** | 18 | **34** ✅ |
| **Сломанных инструментов** | 14 | **0** ✅ |
| **Новые возможности** | - | Tags, Users, Moderate ✅ |

---

## ⚠️ Важно

- ✅ **100% обратно совместим** - все работает как раньше
- ✅ **Без миграций БД** - база данных не изменяется
- ✅ **Без новых зависимостей** - не нужен `pip install`
- ✅ **Без изменений frontend** - пересборка не требуется

---

## 🆘 Если что-то пошло не так

### Откат изменений:

```bash
cd /var/www/sofiya
git log --oneline -5
git revert HEAD
pm2 restart all
```

### Или восстановить из бэкапа:

```bash
cd /var/www/sofiya
ls backups/  # найти нужный бэкап
cp backups/backup_XXXXXXXX_XXXXXX/* backend/app/
pm2 restart all
```

---

## 📚 Документация

- **Установка:** `PATCH_v4.1_TOOLS_FIX.md`
- **Детали:** `FIXES_COMPLETED_2025-10-15.md`
- **Команды:** `SERVER_PATCH_COMMANDS.txt`
- **Анализ:** `TOOLS_COMPARISON_SUMMARY.md`

---

## 📞 Поддержка

**GitHub:** https://github.com/Horosheff/sofa  
**Коммит:** `fix: [PATCH v4.1] Critical tools synchronization fix`

---

**Дата:** 2025-10-15  
**Версия:** v4.1.0  
**Статус:** ✅ READY FOR PRODUCTION

