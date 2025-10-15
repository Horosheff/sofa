# 🤖 Telegram Bot Integration

## Обзор

Добавлена полная интеграция с Telegram Bot API в MCP Platform. Теперь пользователи могут:

- Создавать и настраивать Telegram ботов
- Отправлять сообщения, фото, документы
- Управлять чатами и участниками
- Настраивать webhook'и
- Использовать все возможности Telegram Bot API

## 🚀 Новые возможности

### Backend (Python)
- **50+ Telegram инструментов** в `telegram_tools.py`
- **Интеграция с python-telegram-bot** библиотекой
- **Настройки Telegram** в базе данных
- **MCP протокол** поддержка для Telegram

### Frontend (React/Next.js)
- **Настройки Telegram** в панели настроек
- **Статус подключения** Telegram бота
- **Группировка инструментов** по категориям
- **Инструкции** по созданию ботов

## 📋 Список инструментов

### Основные операции
- `telegram_create_bot` - Создать и настроить бота
- `telegram_send_message` - Отправить сообщение
- `telegram_send_photo` - Отправить фото
- `telegram_send_document` - Отправить документ

### Webhook управление
- `telegram_set_webhook` - Установить webhook
- `telegram_delete_webhook` - Удалить webhook
- `telegram_get_webhook_info` - Информация о webhook

### Информация о боте
- `telegram_get_bot_info` - Информация о боте
- `telegram_get_updates` - Получить обновления
- `telegram_set_commands` - Установить команды
- `telegram_get_commands` - Получить команды

### Управление сообщениями
- `telegram_delete_message` - Удалить сообщение
- `telegram_edit_message` - Редактировать сообщение
- `telegram_pin_message` - Закрепить сообщение
- `telegram_unpin_message` - Открепить сообщение

### Управление чатами
- `telegram_get_chat` - Информация о чате
- `telegram_get_chat_member` - Информация об участнике
- `telegram_ban_chat_member` - Заблокировать участника
- `telegram_unban_chat_member` - Разблокировать участника
- `telegram_promote_chat_member` - Повысить до админа
- `telegram_restrict_chat_member` - Ограничить права

### Ссылки-приглашения
- `telegram_export_chat_invite_link` - Создать ссылку
- `telegram_create_chat_invite_link` - Создать ссылку с настройками
- `telegram_revoke_chat_invite_link` - Отозвать ссылку

### Заявки на вступление
- `telegram_approve_chat_join_request` - Одобрить заявку
- `telegram_decline_chat_join_request` - Отклонить заявку

### Настройки чата
- `telegram_set_chat_photo` - Установить фото чата
- `telegram_delete_chat_photo` - Удалить фото чата
- `telegram_set_chat_title` - Установить название
- `telegram_set_chat_description` - Установить описание
- `telegram_pin_chat_message` - Закрепить сообщение в чате
- `telegram_unpin_chat_message` - Открепить сообщение в чате
- `telegram_unpin_all_chat_messages` - Открепить все сообщения
- `telegram_leave_chat` - Покинуть чат

### Администраторы и участники
- `telegram_get_chat_administrators` - Список администраторов
- `telegram_get_chat_member_count` - Количество участников
- `telegram_get_chat_menu_button` - Кнопка меню чата
- `telegram_set_chat_menu_button` - Установить кнопку меню

### Callback и Inline запросы
- `telegram_answer_callback_query` - Ответить на callback
- `telegram_answer_inline_query` - Ответить на inline запрос

### Опросы и игры
- `telegram_stop_poll` - Остановить опрос
- `telegram_send_poll` - Отправить опрос
- `telegram_send_dice` - Отправить кубик
- `telegram_send_game` - Отправить игру


### Платежи
- `telegram_send_invoice` - Отправить счёт

### Медиа группы
- `telegram_send_media_group` - Отправить группу медиа
- `telegram_send_animation` - Отправить анимацию (GIF)
- `telegram_send_audio` - Отправить аудио
- `telegram_send_video` - Отправить видео
- `telegram_send_video_note` - Отправить видеосообщение
- `telegram_send_voice` - Отправить голосовое сообщение
- `telegram_send_sticker` - Отправить стикер

### Стикеры
- `telegram_get_sticker_set` - Получить набор стикеров
- `telegram_upload_sticker_file` - Загрузить файл стикера
- `telegram_create_new_sticker_set` - Создать набор стикеров
- `telegram_add_sticker_to_set` - Добавить стикер в набор
- `telegram_set_sticker_position_in_set` - Установить позицию стикера
- `telegram_delete_sticker_from_set` - Удалить стикер из набора
- `telegram_set_sticker_set_thumb` - Установить миниатюру набора

### Действия и файлы
- `telegram_send_chat_action` - Отправить действие чата
- `telegram_get_user_profile_photos` - Фото профиля пользователя
- `telegram_get_file` - Получить файл

### Дополнительные функции
- `telegram_kick_chat_member` - Исключить участника
- `telegram_set_chat_administrator_custom_title` - Кастомный титул админа
- `telegram_ban_chat_sender_chat` - Заблокировать отправителя чата
- `telegram_unban_chat_sender_chat` - Разблокировать отправителя чата
- `telegram_set_chat_permissions` - Установить права чата
- `telegram_edit_chat_invite_link` - Редактировать ссылку-приглашение
- `telegram_set_chat_sticker_set` - Установить набор стикеров чата
- `telegram_delete_chat_sticker_set` - Удалить набор стикеров чата

## 🛠️ Установка и настройка

### 1. Установка зависимостей

```bash
cd backend
pip install python-telegram-bot
```

### 2. Миграция базы данных

```bash
cd backend
python migrate_telegram_fields.py
```

### 3. Настройка в интерфейсе

1. Зайдите в **Настройки** на сайте
2. Найдите секцию **🤖 Telegram Bot настройки**
3. Следуйте инструкциям по созданию бота
4. Вставьте токен бота от @BotFather
5. Сохраните настройки

## 📱 Создание Telegram бота

### Шаг 1: Создание бота
1. Найдите **@BotFather** в Telegram
2. Отправьте команду `/newbot`
3. Введите имя для бота (например: "My Awesome Bot")
4. Введите username для бота (например: "my_awesome_bot")
5. Скопируйте полученный токен

### Шаг 2: Настройка в MCP Platform
1. Вставьте токен в поле **"Токен бота"**
2. При необходимости настройте **Webhook URL**
3. Сохраните настройки

## 🔧 Использование

### Через MCP протокол
```json
{
  "tool": "telegram_send_message",
  "params": {
    "chat_id": "@username",
    "text": "Привет из MCP Platform!",
    "parse_mode": "HTML"
  }
}
```

### Через веб-интерфейс
1. Перейдите в раздел **Инструменты**
2. Найдите секцию **🤖 Telegram**
3. Выберите нужный инструмент
4. Заполните параметры
5. Нажмите **"Выполнить"**

## 🔒 Безопасность

- **Токены ботов** хранятся в зашифрованном виде
- **Webhook секреты** защищены
- **Доступ** только для авторизованных пользователей
- **Логирование** всех операций

## 📊 Мониторинг

- **Статус подключения** в панели инструментов
- **Логи операций** в админ-панели
- **Статистика использования** в профиле пользователя

## 🚀 Примеры использования

### Отправка сообщения
```json
{
  "tool": "telegram_send_message",
  "params": {
    "chat_id": "-1001234567890",
    "text": "📢 <b>Важное уведомление</b>\n\nНовая статья опубликована!",
    "parse_mode": "HTML"
  }
}
```

### Отправка фото
```json
{
  "tool": "telegram_send_photo",
  "params": {
    "chat_id": "@channel",
    "photo": "https://example.com/image.jpg",
    "caption": "Красивое фото!"
  }
}
```

### Управление чатом
```json
{
  "tool": "telegram_set_chat_title",
  "params": {
    "chat_id": "-1001234567890",
    "title": "Новое название чата"
  }
}
```

## 🆘 Поддержка

При возникновении проблем:

1. **Проверьте токен бота** - он должен быть действительным
2. **Убедитесь в правах бота** - бот должен быть администратором в чатах
3. **Проверьте webhook** - если используете webhook, убедитесь в правильности URL
4. **Посмотрите логи** - в админ-панели есть подробные логи операций

## 📈 Планы развития

- [ ] **Inline клавиатуры** для интерактивных сообщений
- [ ] **Планировщик сообщений** для отложенной отправки
- [ ] **Шаблоны сообщений** для быстрого создания
- [ ] **Аналитика ботов** с детальной статистикой
- [ ] **Интеграция с WordPress** для автоматических уведомлений
