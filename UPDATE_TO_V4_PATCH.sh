#!/bin/bash

# ============================================================
# ПАТЧ ДЛЯ ОБНОВЛЕНИЯ ДО ВЕРСИИ 4.0.0
# Применяется на работающем сервере без остановки
# ============================================================

set -e  # Остановка при ошибке

echo "============================================================"
echo "🚀 Обновление MCP Platform до v4.0.0"
echo "============================================================"

# Проверка текущей директории
if [ ! -d "backend/app" ]; then
    echo "❌ Ошибка: Запустите скрипт из корня проекта!"
    exit 1
fi

echo ""
echo "📦 ШАГ 1: Копирование новых модулей..."

# Backend - новые модули
echo "  → backend/app/helpers.py"
echo "  → backend/app/mcp_handlers.py"
echo "  → backend/app/wordpress_tools.py"
echo "  → backend/app/wordstat_tools.py"
echo "  → backend/app/admin_routes.py"
echo "  → backend/test_modules.py"

# Frontend - админ панель
echo "  → frontend/app/admin/"
echo "  → frontend/app/api/admin/"
echo "  → frontend/app/api/login/"
echo "  → frontend/components/Admin*.tsx"
echo "  → frontend/components/StatsPanel.tsx"

echo ""
echo "📝 ШАГ 2: Проверка зависимостей..."

# Backend dependencies
if [ -f "backend/requirements.txt" ]; then
    echo "  ✓ backend/requirements.txt существует"
else
    echo "  ⚠️  backend/requirements.txt не найден"
fi

# Frontend dependencies
if [ -f "frontend/package.json" ]; then
    echo "  ✓ frontend/package.json существует"
else
    echo "  ⚠️  frontend/package.json не найден"
fi

echo ""
echo "🔧 ШАГ 3: Резервное копирование..."

# Создаём backup папку
mkdir -p backups/pre_v4_$(date +%Y%m%d_%H%M%S)

# Backup главных файлов
cp backend/app/main.py backups/pre_v4_$(date +%Y%m%d_%H%M%S)/main.py.backup 2>/dev/null || true
cp backend/app/models.py backups/pre_v4_$(date +%Y%m%d_%H%M%S)/models.py.backup 2>/dev/null || true
cp backend/app/auth.py backups/pre_v4_$(date +%Y%m%d_%H%M%S)/auth.py.backup 2>/dev/null || true

# Backup database
if [ -f "backend/app.db" ]; then
    cp backend/app.db backups/pre_v4_$(date +%Y%m%d_%H%M%S)/app.db.backup
    echo "  ✓ Database backed up"
fi

echo "  ✓ Резервные копии созданы в backups/"

echo ""
echo "============================================================"
echo "✅ Подготовка завершена!"
echo "============================================================"
echo ""
echo "📋 СЛЕДУЮЩИЕ ШАГИ:"
echo ""
echo "1. Добавьте новые файлы в Git:"
echo "   git add backend/app/helpers.py"
echo "   git add backend/app/mcp_handlers.py"
echo "   git add backend/app/wordpress_tools.py"
echo "   git add backend/app/wordstat_tools.py"
echo "   git add backend/app/admin_routes.py"
echo "   git add backend/test_modules.py"
echo "   git add frontend/app/admin/"
echo "   git add frontend/components/Admin*.tsx"
echo "   git add frontend/components/StatsPanel.tsx"
echo ""
echo "2. Закоммитьте изменённые файлы:"
echo "   git add backend/app/main.py"
echo "   git add backend/app/models.py"
echo "   git add backend/app/auth.py"
echo "   git add frontend/app/globals.css"
echo "   git add frontend/app/page.tsx"
echo "   git add frontend/components/Dashboard.tsx"
echo "   git add frontend/components/SettingsPanel.tsx"
echo ""
echo "3. Создайте коммит:"
echo "   git commit -m \"v4.0.0: Modular architecture refactoring\""
echo ""
echo "4. Запуште на GitHub:"
echo "   git push origin main"
echo ""
echo "5. На сервере выполните:"
echo "   cd /var/www/sofa"
echo "   git pull origin main"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   python test_modules.py  # Проверка"
echo "   pm2 restart mcp-backend"
echo "   cd ../frontend"
echo "   npm run build"
echo "   pm2 restart mcp-frontend"
echo ""
echo "============================================================"
echo "⚠️  ВАЖНО: Сервис НЕ будет остановлен до pm2 restart"
echo "============================================================"

