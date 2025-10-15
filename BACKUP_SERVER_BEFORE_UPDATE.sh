#!/bin/bash

# 🚀 Скрипт резервного копирования сервера перед обновлением
# Создает полную резервную копию всех компонентов системы

set -e  # Остановить при ошибке

echo "🔒 Начинаем резервное копирование сервера..."

# Создаем папку для бэкапа с временной меткой
BACKUP_DIR="/opt/backups/backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "📁 Создана папка для бэкапа: $BACKUP_DIR"

# 1. Резервная копия базы данных
echo "🗄️ Создаем резервную копию базы данных..."
if [ -f "/opt/sofiya/backend/app.db" ]; then
    cp /opt/sofiya/backend/app.db "$BACKUP_DIR/app.db"
    sqlite3 /opt/sofiya/backend/app.db ".dump" > "$BACKUP_DIR/database_backup.sql"
    echo "✅ База данных скопирована"
else
    echo "⚠️ База данных не найдена"
fi

# 2. Резервная копия всего проекта
echo "📦 Создаем архив проекта..."
cd /opt
tar -czf "$BACKUP_DIR/sofiya_backup.tar.gz" sofiya/
echo "✅ Проект заархивирован"

# 3. Git репозиторий
echo "🔧 Создаем git bundle..."
cd /opt/sofiya
git bundle create "$BACKUP_DIR/sofiya_git_backup.bundle" --all
echo "✅ Git репозиторий сохранен"

# 4. PM2 конфигурация
echo "⚙️ Сохраняем PM2 конфигурацию..."
pm2 save
cp ~/.pm2/dump.pm2 "$BACKUP_DIR/pm2_dump.pm2" 2>/dev/null || echo "⚠️ PM2 конфигурация не найдена"

# 5. Текущий статус процессов
echo "📊 Сохраняем статус процессов..."
pm2 status > "$BACKUP_DIR/pm2_status.txt"
pm2 list > "$BACKUP_DIR/pm2_list.txt"

# 6. Системная информация
echo "💻 Сохраняем системную информацию..."
uname -a > "$BACKUP_DIR/system_info.txt"
df -h > "$BACKUP_DIR/disk_usage.txt"
free -h > "$BACKUP_DIR/memory_usage.txt"
ps aux > "$BACKUP_DIR/running_processes.txt"

# 7. Nginx конфигурация (если есть)
echo "🌐 Копируем Nginx конфигурацию..."
if [ -d "/etc/nginx/sites-available" ]; then
    cp -r /etc/nginx/sites-available "$BACKUP_DIR/nginx_sites_available" 2>/dev/null || true
    cp -r /etc/nginx/sites-enabled "$BACKUP_DIR/nginx_sites_enabled" 2>/dev/null || true
    echo "✅ Nginx конфигурация скопирована"
fi

# 8. Логи (последние 1000 строк)
echo "📝 Сохраняем логи..."
pm2 logs backend --lines 1000 --nostream > "$BACKUP_DIR/backend_logs.txt" 2>/dev/null || true
pm2 logs frontend --lines 1000 --nostream > "$BACKUP_DIR/frontend_logs.txt" 2>/dev/null || true

# 9. Переменные окружения
echo "🔐 Сохраняем переменные окружения..."
env > "$BACKUP_DIR/environment_variables.txt"

# 10. Создаем README с информацией о бэкапе
cat > "$BACKUP_DIR/README.md" << EOF
# 🔒 Резервная копия сервера

**Дата создания:** $(date)
**Сервер:** $(hostname)
**Пользователь:** $(whoami)

## 📁 Содержимое бэкапа:

- \`app.db\` - База данных SQLite
- \`database_backup.sql\` - SQL дамп базы данных
- \`sofiya_backup.tar.gz\` - Полный архив проекта
- \`sofiya_git_backup.bundle\` - Git репозиторий
- \`pm2_dump.pm2\` - Конфигурация PM2
- \`pm2_status.txt\` - Статус PM2 процессов
- \`system_info.txt\` - Информация о системе
- \`disk_usage.txt\` - Использование диска
- \`memory_usage.txt\` - Использование памяти
- \`running_processes.txt\` - Запущенные процессы
- \`environment_variables.txt\` - Переменные окружения
- \`backend_logs.txt\` - Логи backend
- \`frontend_logs.txt\` - Логи frontend

## 🔄 Восстановление:

### Восстановление базы данных:
\`\`\`bash
cp app.db /opt/sofiya/backend/app.db
\`\`\`

### Восстановление проекта:
\`\`\`bash
cd /opt
tar -xzf sofiya_backup.tar.gz
\`\`\`

### Восстановление PM2:
\`\`\`bash
pm2 resurrect /path/to/pm2_dump.pm2
\`\`\`

### Восстановление Git:
\`\`\`bash
cd /opt/sofiya
git clone sofiya_git_backup.bundle restored_project
\`\`\`

---
**Создано автоматически скриптом резервного копирования**
EOF

# 11. Создаем архив всего бэкапа
echo "📦 Создаем финальный архив бэкапа..."
cd /opt/backups
tar -czf "backup_$(date +%Y%m%d_%H%M%S).tar.gz" "backup_$(date +%Y%m%d_%H%M%S)"
echo "✅ Финальный архив создан: backup_$(date +%Y%m%d_%H%M%S).tar.gz"

# 12. Показываем размер бэкапа
echo "📊 Информация о бэкапе:"
du -sh "$BACKUP_DIR"
du -sh "/opt/backups/backup_$(date +%Y%m%d_%H%M%S).tar.gz"

echo ""
echo "🎉 Резервное копирование завершено!"
echo "📁 Папка бэкапа: $BACKUP_DIR"
echo "📦 Архив бэкапа: /opt/backups/backup_$(date +%Y%m%d_%H%M%S).tar.gz"
echo ""
echo "💡 Для восстановления используйте команды из README.md в папке бэкапа"
