#!/bin/bash

echo "🔍 Проверяем структуру файлов перед сборкой..."

echo "📁 Содержимое директории:"
ls -la

echo "📁 Содержимое store/:"
ls -la store/ || echo "❌ Директория store/ не найдена"

echo "📁 Содержимое components/:"
ls -la components/ || echo "❌ Директория components/ не найдена"

echo "📄 Содержимое tsconfig.json:"
cat tsconfig.json || echo "❌ tsconfig.json не найден"

echo "🔧 Пробуем собрать проект..."
npm run build
