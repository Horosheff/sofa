# 🚀 Прямое подключение к MCP серверу (без OAuth)

## ✅ ДА! Можно использовать прямую ссылку!

### 🔗 Ваша персональная ссылка:
```
https://mcp-kv.ru/mcp/sse/horosheff-8-43e13a30
```

## 📋 Как получить JWT токен:

### 1. Войди в систему:
```bash
curl -X POST https://mcp-kv.ru/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"your@email.com","password":"your_password"}'
```

### 2. Получи персональный manifest:
```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  https://mcp-kv.ru/user/mcp-manifest
```

### 3. Используй данные из manifest:
- **SSE URL:** `https://mcp-kv.ru/mcp/sse/horosheff-8-43e13a30`
- **JWT Token:** `eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...`
- **Header:** `Authorization: Bearer YOUR_TOKEN`

## 🎯 Где использовать:

### ChatGPT:
1. Открой Settings → Connectors
2. Добавь новый коннектор
3. URL: `https://mcp-kv.ru/mcp/sse/horosheff-8-43e13a30`
4. Authorization: `Bearer YOUR_JWT_TOKEN`

### Make.com:
1. Создай MCP connection
2. URL: `https://mcp-kv.ru/mcp/sse/horosheff-8-43e13a30`
3. Headers: `Authorization: Bearer YOUR_JWT_TOKEN`

### Любой MCP клиент:
```bash
curl -N -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  https://mcp-kv.ru/mcp/sse/horosheff-8-43e13a30
```

## 🔧 Доступные инструменты (25 штук):

### WordPress (15 инструментов):
- `wordpress_get_posts` - Получить посты
- `wordpress_create_post` - Создать пост
- `wordpress_update_post` - Обновить пост
- `wordpress_delete_post` - Удалить пост
- `wordpress_get_pages` - Получить страницы
- `wordpress_create_page` - Создать страницу
- `wordpress_get_categories` - Получить категории
- `wordpress_create_category` - Создать категорию
- `wordpress_get_tags` - Получить теги
- `wordpress_create_tag` - Создать тег
- `wordpress_get_media` - Получить медиафайлы
- `wordpress_upload_media` - Загрузить медиафайл
- `wordpress_get_users` - Получить пользователей
- `wordpress_get_comments` - Получить комментарии
- `wordpress_moderate_comment` - Модерировать комментарий

### Yandex Wordstat (10 инструментов):
- `wordstat_get_user_info` - Информация о пользователе
- `wordstat_get_regions_tree` - Дерево регионов
- `wordstat_get_top_requests` - Топ запросов
- `wordstat_get_dynamics` - Динамика запросов
- `wordstat_get_regions` - Список регионов
- `wordstat_auto_setup` - Автонастройка токена
- `wordstat_get_competitors` - Анализ конкурентов
- `wordstat_get_related_queries` - Похожие запросы
- `wordstat_get_geography` - География запросов
- `wordstat_export_data` - Экспорт данных

## ⚡ Преимущества прямого доступа:

✅ **Нет OAuth** - просто URL + токен  
✅ **Долгосрочный токен** - действует 1 год  
✅ **Персональный доступ** - только твои данные  
✅ **Простота настройки** - один URL  
✅ **25 инструментов** - WordPress + Wordstat  

## 🔒 Безопасность:

- JWT токен привязан к твоему аккаунту
- Доступ только к твоим WordPress сайтам
- Токен можно отозвать в настройках
- Все запросы логируются

## 🆘 Поддержка:

Если что-то не работает:
1. Проверь, что токен не истек
2. Убедись, что connector_id правильный
3. Проверь настройки WordPress/Wordstat
4. Посмотри логи: `journalctl -u sofiya-backend -f`
