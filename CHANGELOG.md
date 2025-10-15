# Changelog

Все значимые изменения в этом проекте будут документированы в этом файле.

Формат основан на [Keep a Changelog](https://keepachangelog.com/ru/1.0.0/),
и этот проект придерживается [Semantic Versioning](https://semver.org/lang/ru/).

---

## [3.0.0] - 2025-10-15 - 🎉 СТАБИЛЬНАЯ ВЕРСИЯ

### ✅ Добавлено
- **Все 5 методов Yandex Wordstat API v1 полностью работают:**
  - `wordstat_get_user_info` - информация о пользователе и квотах
  - `wordstat_get_regions_tree` - дерево регионов Yandex
  - `wordstat_get_top_requests` - топ поисковых запросов
  - `wordstat_get_regions` - распределение по регионам
  - `wordstat_get_dynamics` - динамика запросов по времени
- Подробная документация `WORDSTAT_API_STATUS.md` со всеми примерами
- Команды для обновления сервера `UPDATE_COMMANDS.txt`
- Скрипт автоматического обновления `UPDATE_SERVER_NOW.sh`
- Детальные release notes `RELEASE_v3.0.0.md`
- Badge в README для статуса Wordstat API

### 🐛 Исправлено
- **Критические баги:**
  - `'list' object has no attribute 'get'` в `wordstat_get_regions`
  - `'list' object has no attribute 'get'` в `wordstat_get_regions_tree`
  - Неправильная обработка ответа API (список вместо объекта)
  - Неправильные имена полей (`id`/`name` → `value`/`label`)
  - Обработка `children: null` в дереве регионов
- **Параметры API:**
  - Исправлен параметр `devices`: теперь используется `phone`/`tablet` вместо `mobile`
  - Enum для `devices`: `all`, `desktop`, `phone`, `tablet`
  - Правильные имена параметров: `phrase`, `numPhrases`, `regionType`, `fromDate`
- **OAuth flow:**
  - 404 ошибка на frontend для `/api/oauth/yandex/callback`
  - Отсутствующий столбец `wordstat_token_expires` в БД

### 📝 Улучшено
- Подробное логирование типов данных в ответах API
- Проверка типов данных перед обработкой (`isinstance()`)
- Безопасный доступ к полям через `.get()` с fallback значениями
- Обработка исключений с полным stack trace
- Документация с реальными примерами запросов и ответов

### 🔧 Технические изменения
- Добавлены описания для всех параметров в `inputSchema`
- Ограничение дерева регионов: 20 на корневом уровне (для читаемости)
- Изоляция токенов Wordstat по пользователям
- Timeout 30 секунд для всех HTTP запросов

---

## [2.0.0] - 2025-10-15 - 🎨 Дизайн и UX

### ✅ Добавлено
- **Glassmorphism UI Design:**
  - Lava Lamp Background - анимированный фон
  - Matrix Effect - эффект падающих символов
  - Frosted glass effect с размытием
  - Messenger-style toast notifications
- **Новая главная страница:**
  - Название "ВСЁ ПОДКЛЮЧЕНО" by Kov4eg
  - Асимметричный двухколоночный макет
  - Иконки социальных сетей (Telegram, VK)
- **OAuth интеграция:**
  - Ручной OAuth flow для Wordstat
  - Генерация и копирование ссылки авторизации
  - Поле для ввода кода авторизации

### 📝 Улучшено
- Полностью адаптивный дизайн для мобильных устройств
- Упрощенная навигация (Tools + Settings)
- 3-колоночная сетка для инструментов
- Пропорциональная ширина header
- Анимированный статус MCP сервера

### 🔧 Удалено
- Отдельная вкладка "Wordstat OAuth" (перенесено в Settings)
- WordPress и Wordstat статусы из header (оставлен только MCP)

---

## [1.0.0] - 2025-10-10 - 🚀 Первый релиз

### ✅ Добавлено
- Базовая архитектура MCP сервера
- FastAPI backend с JWT аутентификацией
- Next.js frontend
- WordPress API интеграция (get_posts, create_post)
- SQLite база данных
- Базовый UI с формами логина/регистрации
- Панель управления (Dashboard)
- Настройки пользователя

### 🔐 Безопасность
- JWT токены для аутентификации
- Bcrypt для хеширования паролей
- HTTPS на production
- Secure cookies

---

## Типы изменений

- `✅ Добавлено` - новые функции
- `📝 Улучшено` - изменения существующей функциональности
- `🐛 Исправлено` - исправление багов
- `🔒 Безопасность` - исправления уязвимостей
- `🔧 Удалено` - удаленная функциональность
- `⚠️ Устарело` - функции, которые скоро будут удалены

---

## Ссылки

- [v3.0.0] - https://github.com/Horosheff/sofa/releases/tag/v3.0.0
- [v2.0.0] - https://github.com/Horosheff/sofa/releases/tag/v2.0.0
- [v1.0.0] - https://github.com/Horosheff/sofa/releases/tag/v1.0.0
