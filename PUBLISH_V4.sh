#!/bin/bash

# ============================================================
# ПУБЛИКАЦИЯ ВЕРСИИ 4.0.0 НА GITHUB
# ============================================================

echo "============================================================"
echo "📦 Публикация v4.0.0 на GitHub"
echo "============================================================"

# Проверка git статуса
echo ""
echo "📊 Текущий статус Git:"
git status --short

echo ""
echo "➕ Добавление НОВЫХ файлов..."

# Backend - новые модули
git add backend/app/helpers.py
git add backend/app/mcp_handlers.py
git add backend/app/wordpress_tools.py
git add backend/app/wordstat_tools.py
git add backend/app/admin_routes.py
git add backend/test_modules.py
git add backend/TEST_REPORT.md

# Frontend - админ панель
git add frontend/app/admin/
git add frontend/app/api/admin/
git add frontend/app/api/login/
git add frontend/components/AdminPanel.tsx
git add frontend/components/AdminDashboard.tsx
git add frontend/components/AdminUsersPanel.tsx
git add frontend/components/AdminLogsPanel.tsx
git add frontend/components/StatsPanel.tsx

# Документация
git add RELEASE_NOTES_v4.md
git add DEPLOY_v4.md
git add UPDATE_TO_V4_PATCH.sh
git add FILES_TO_ADD_v4.txt
git add PUBLISH_V4.sh

echo "✓ Новые файлы добавлены"

echo ""
echo "✏️  Добавление ИЗМЕНЁННЫХ файлов..."

# Backend - изменённые
git add backend/app/main.py
git add backend/app/models.py
git add backend/app/auth.py

# Frontend - изменённые
git add frontend/app/globals.css
git add frontend/app/page.tsx
git add frontend/components/Dashboard.tsx
git add frontend/components/SettingsPanel.tsx
git add frontend/package.json

echo "✓ Изменённые файлы добавлены"

echo ""
echo "🗑️  Удаление НЕНУЖНЫХ файлов..."

# Удаляем старые deployment скрипты
git rm -f deploy.sh 2>/dev/null || true
git rm -f quick-deploy.sh 2>/dev/null || true
git rm -f cloud-deploy-commands.sh 2>/dev/null || true
git rm -f deploy-ubuntu.sh 2>/dev/null || true
git rm -f install-ubuntu.sh 2>/dev/null || true
git rm -f update-all-files.sh 2>/dev/null || true
git rm -f upload-to-server.sh 2>/dev/null || true
git rm -f restart-backend.sh 2>/dev/null || true
git rm -f rebuild-frontend.sh 2>/dev/null || true

# Удаляем старые документы
git rm -f DOCKER_README.md 2>/dev/null || true
git rm -f SERVER_DEPLOYMENT.md 2>/dev/null || true
git rm -f QUICK_DEPLOY.md 2>/dev/null || true
git rm -f MCP_SSE_GUIDE.md 2>/dev/null || true
git rm -f GITHUB_RELEASE_v3.0.0.md 2>/dev/null || true
git rm -f DEPLOY_v3.0.0_NOW.txt 2>/dev/null || true

# Удаляем Docker файлы
git rm -f docker-compose.yml 2>/dev/null || true
git rm -f backend/Dockerfile 2>/dev/null || true
git rm -f frontend/Dockerfile 2>/dev/null || true
git rm -f env.production 2>/dev/null || true

# Удаляем другие ненужные файлы
git rm -f backend/init_db.py 2>/dev/null || true
git rm -f frontend/server.js 2>/dev/null || true
git rm -f frontend/test-build.sh 2>/dev/null || true
git rm -f sofiya-update.tar.gz 2>/dev/null || true
git rm -f package-lock.json 2>/dev/null || true

echo "✓ Ненужные файлы удалены"

echo ""
echo "📊 Финальный статус:"
git status --short

echo ""
echo "============================================================"
echo "✅ Файлы подготовлены!"
echo "============================================================"
echo ""
echo "📋 СЛЕДУЮЩИЕ ШАГИ:"
echo ""
echo "1. Проверьте изменения:"
echo "   git diff --cached --stat"
echo ""
echo "2. Создайте коммит:"
echo '   git commit -m "v4.0.0: Modular architecture refactoring'
echo ''
echo '   BREAKING CHANGES:'
echo '   - Backend разбит на модули: helpers, mcp_handlers, wordpress_tools, wordstat_tools'
echo '   - Добавлена админ панель для управления платформой'
echo '   - Улучшена безопасность: validation, sanitization, rate limiting'
echo '   - Добавлены метрики API calls'
echo '   - 37 автоматических тестов (100% pass rate)'
echo '   '
echo '   NEW:'
echo '   - helpers.py: 15+ utility functions'
echo '   - mcp_handlers.py: SSE Manager, OAuth Store, MCP tools'
echo '   - wordpress_tools.py: 18 WordPress instruments'
echo '   - wordstat_tools.py: 7 Wordstat instruments'
echo '   - admin_routes.py: Admin API endpoints'
echo '   - Admin panel: user management, logs, statistics'
echo '   '
echo '   IMPROVED:'
echo '   - main.py: -443 lines (-19% code)'
echo '   - Security: URL/email validation, XSS protection'
echo '   - Monitoring: API metrics, sensitive data masking'
echo '   - Testing: 37 automated tests'
echo '   '
echo '   DOCS:'
echo '   - RELEASE_NOTES_v4.md: Full changelog'
echo '   - DEPLOY_v4.md: Deployment guide'
echo '   - TEST_REPORT.md: Test results'"'
echo ""
echo "3. Создайте тег:"
echo "   git tag -a v4.0.0 -m \"Version 4.0.0 - Modular Architecture\""
echo ""
echo "4. Отправьте на GitHub:"
echo "   git push origin main"
echo "   git push origin v4.0.0"
echo ""
echo "5. Деплой на сервер:"
echo "   ssh root@mcp-kv.ru"
echo "   cd /var/www/sofa"
echo "   git pull origin main"
echo "   cd backend && source venv/bin/activate"
echo "   python test_modules.py"
echo "   pm2 restart mcp-backend"
echo "   cd ../frontend && npm run build"
echo "   pm2 restart mcp-frontend"
echo ""
echo "============================================================"

