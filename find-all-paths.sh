#!/bin/bash

echo "🔍 НАХОДИМ ВСЕ ПУТИ НА СЕРВЕРЕ..."

echo "📁 Backend файлы:"
find /opt/sofiya -name "*.py" -type f

echo ""
echo "📁 Frontend файлы:"
find /opt/sofiya -name "*.tsx" -type f
find /opt/sofiya -name "*.ts" -type f

echo ""
echo "📁 Конфигурационные файлы:"
find /opt/sofiya -name "*.json" -type f
find /opt/sofiya -name "*.js" -type f
find /opt/sofiya -name "*.sh" -type f

echo ""
echo "📁 Системные файлы:"
find /opt/sofiya -name "*.service" -type f
find /opt/sofiya -name "*.conf" -type f
find /opt/sofiya -name "*.env" -type f

echo ""
echo "📁 База данных:"
find /opt/sofiya -name "*.db" -type f
find /opt/sofiya -name "*.sqlite*" -type f
