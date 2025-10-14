#!/bin/bash

echo "🔧 ОБНОВЛЯЕМ ВСЕ ФАЙЛЫ НА СЕРВЕРЕ..."

# 1. Останавливаем сервисы
echo "⏹️ Останавливаем сервисы..."
systemctl stop sofiya-backend sofiya-frontend

# 2. Скачиваем исправленные файлы
echo "📥 Скачиваем исправленные файлы..."
wget -q https://raw.githubusercontent.com/Horosheff/sofiya/main/backend/app/main.py -O /tmp/main.py
wget -q https://raw.githubusercontent.com/Horosheff/sofiya/main/frontend/components/SettingsPanel.tsx -O /tmp/SettingsPanel.tsx
wget -q https://raw.githubusercontent.com/Horosheff/sofiya/main/frontend/components/LoginForm.tsx -O /tmp/LoginForm.tsx
wget -q https://raw.githubusercontent.com/Horosheff/sofiya/main/frontend/components/RegisterForm.tsx -O /tmp/RegisterForm.tsx

# 3. Заменяем файлы
echo "📋 Заменяем файлы..."
cp /tmp/main.py /opt/sofiya/backend/app/main.py
cp /tmp/SettingsPanel.tsx /opt/sofiya/frontend/components/SettingsPanel.tsx
cp /tmp/LoginForm.tsx /opt/sofiya/frontend/components/LoginForm.tsx
cp /tmp/RegisterForm.tsx /opt/sofiya/frontend/components/RegisterForm.tsx

# 4. Очищаем кэш Next.js
echo "🧹 Очищаем кэш Next.js..."
cd /opt/sofiya/frontend
rm -rf .next
rm -rf node_modules/.cache

# 5. Пересобираем frontend
echo "🔨 Пересобираем frontend..."
npm run build

# 6. Запускаем сервисы
echo "▶️ Запускаем сервисы..."
systemctl start sofiya-backend sofiya-frontend

# 7. Проверяем статус
echo "✅ Проверяем статус..."
systemctl status sofiya-backend sofiya-frontend --no-pager -l

echo "🎉 ВСЕ ФАЙЛЫ ОБНОВЛЕНЫ!"
