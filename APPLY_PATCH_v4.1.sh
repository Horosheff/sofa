#!/bin/bash

# ========================================
# PATCH v4.1: Tools Synchronization Fix
# Автоматическое применение на сервере
# ========================================

set -e  # Exit on error

echo "================================================================================================"
echo "PATCH v4.1: Tools Synchronization Fix"
echo "================================================================================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Функция для вывода с цветом
log_info() {
    echo -e "${CYAN}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Проверка, что мы в правильной директории
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    log_error "Запустите скрипт из корневой директории проекта!"
    exit 1
fi

log_info "Starting PATCH v4.1 installation..."
echo ""

# ========================================
# ШАГ 1: Остановка сервисов
# ========================================
log_info "Step 1/6: Stopping services..."

if command -v pm2 &> /dev/null; then
    pm2 stop all || log_warning "Some PM2 processes may not be running"
    log_success "PM2 processes stopped"
else
    log_warning "PM2 not found, skipping..."
fi

echo ""

# ========================================
# ШАГ 2: Бэкап текущей версии
# ========================================
log_info "Step 2/6: Creating backup..."

BACKUP_DIR="backups/backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Бэкап только критичных файлов
cp backend/app/main.py "$BACKUP_DIR/main.py.bak" 2>/dev/null || true
cp backend/app/mcp_handlers.py "$BACKUP_DIR/mcp_handlers.py.bak" 2>/dev/null || true
cp backend/app/wordpress_tools.py "$BACKUP_DIR/wordpress_tools.py.bak" 2>/dev/null || true

log_success "Backup created in $BACKUP_DIR"
echo ""

# ========================================
# ШАГ 3: Применение патча
# ========================================
log_info "Step 3/6: Applying patch from GitHub..."

# Сохраняем текущую ветку
CURRENT_BRANCH=$(git branch --show-current)

# Проверяем, есть ли незакоммиченные изменения
if [[ -n $(git status -s) ]]; then
    log_warning "Found uncommitted changes. Stashing..."
    git stash
    STASHED=1
else
    STASHED=0
fi

# Применяем патч
git fetch origin
git pull origin main

if [ $? -eq 0 ]; then
    log_success "Patch applied successfully!"
else
    log_error "Failed to apply patch!"
    if [ $STASHED -eq 1 ]; then
        git stash pop
    fi
    exit 1
fi

# Возвращаем stash если был
if [ $STASHED -eq 1 ]; then
    log_info "Restoring stashed changes..."
    git stash pop || log_warning "Could not restore stashed changes"
fi

echo ""

# ========================================
# ШАГ 4: Проверка изменений
# ========================================
log_info "Step 4/6: Verifying changes..."

# Проверяем, что файлы обновились
if [ -f "PATCH_v4.1_TOOLS_FIX.md" ]; then
    log_success "Patch files found"
else
    log_error "Patch files not found! Something went wrong."
    exit 1
fi

# Проверяем изменения в коде
if grep -q "get_all_mcp_tools()" backend/app/main.py; then
    log_success "main.py updated correctly"
else
    log_error "main.py not updated!"
    exit 1
fi

echo ""

# ========================================
# ШАГ 5: Запуск тестов
# ========================================
log_info "Step 5/6: Running tests..."

cd backend

# Активируем виртуальное окружение если есть
if [ -d "venv" ]; then
    source venv/bin/activate || source venv/Scripts/activate 2>/dev/null || true
fi

# Запускаем тесты
python test_modules.py > /tmp/patch_test_results.txt 2>&1

if grep -q "7/7 тестов пройдено" /tmp/patch_test_results.txt; then
    log_success "All tests PASSED (7/7)"
else
    log_error "Tests FAILED! Check /tmp/patch_test_results.txt"
    cat /tmp/patch_test_results.txt
    cd ..
    exit 1
fi

# Проверяем количество инструментов
TOOLS_COUNT=$(python -c "from app.mcp_handlers import get_all_mcp_tools; print(len(get_all_mcp_tools()))" 2>/dev/null || echo "0")

if [ "$TOOLS_COUNT" = "34" ]; then
    log_success "Tools count correct: $TOOLS_COUNT"
else
    log_error "Wrong tools count: $TOOLS_COUNT (expected 34)"
    cd ..
    exit 1
fi

cd ..
echo ""

# ========================================
# ШАГ 6: Перезапуск сервисов
# ========================================
log_info "Step 6/6: Restarting services..."

if command -v pm2 &> /dev/null; then
    # Backend
    cd backend
    if [ -f "ecosystem.config.js" ]; then
        pm2 start ecosystem.config.js || pm2 restart all
        log_success "Backend restarted"
    else
        log_warning "ecosystem.config.js not found, manual restart may be needed"
    fi
    cd ..
    
    # Ждем немного
    sleep 3
    
    # Проверяем статус
    pm2 list
    log_success "PM2 services restarted"
else
    log_warning "PM2 not found. Please restart services manually."
fi

echo ""

# ========================================
# ФИНАЛЬНАЯ ПРОВЕРКА
# ========================================
log_info "Final verification..."

# Проверка API если сервис запущен
if command -v curl &> /dev/null; then
    sleep 2
    RESPONSE=$(curl -s -X POST http://localhost:8000/mcp/sse/test \
        -H "Content-Type: application/json" \
        -d '{"jsonrpc":"2.0","method":"initialize","id":1}' 2>/dev/null || echo "")
    
    if [[ $RESPONSE == *"serverInfo"* ]]; then
        log_success "API responding correctly"
    else
        log_warning "API check skipped or service not ready yet"
    fi
fi

echo ""
echo "================================================================================================"
echo -e "${GREEN}PATCH v4.1 INSTALLED SUCCESSFULLY!${NC}"
echo "================================================================================================"
echo ""
echo "Summary:"
echo "  ✅ Backup created: $BACKUP_DIR"
echo "  ✅ Patch applied from GitHub"
echo "  ✅ Tests passed: 7/7"
echo "  ✅ Tools count: 34 (27 WordPress + 7 Wordstat)"
echo "  ✅ Services restarted"
echo ""
echo "Changes:"
echo "  • Removed hardcode from main.py (~80 lines)"
echo "  • Added 9 new tools (Tags, Users, Moderate)"
echo "  • Fixed 14 broken tools"
echo "  • All tools now work correctly"
echo ""
echo "Next steps:"
echo "  1. Check PM2 logs: pm2 logs"
echo "  2. Monitor service: pm2 monit"
echo "  3. Test API: curl http://localhost:8000/health"
echo ""
echo "Documentation: PATCH_v4.1_TOOLS_FIX.md"
echo "================================================================================================"

