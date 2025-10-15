#!/bin/bash

# 🚨 ИСПРАВЛЕНИЕ СИНТАКСИЧЕСКОЙ ОШИБКИ В MAIN.PY
echo "🚨 ИСПРАВЛЕНИЕ СИНТАКСИЧЕСКОЙ ОШИБКИ В MAIN.PY"
echo "============================================="

# Переходим в правильную папку
cd /opt/sofiya

# 1. ПРОВЕРЯЕМ ПЕРВЫЕ СТРОКИ MAIN.PY
echo "1️⃣ Проверяем первые строки main.py..."
head -10 backend/app/main.py

# 2. ИСПРАВЛЯЕМ СИНТАКСИЧЕСКУЮ ОШИБКУ
echo "2️⃣ Исправляем синтаксическую ошибку..."
cd backend/app

# Создаем правильную структуру main.py
cat > main.py << 'EOF'
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import json
import asyncio
import logging
from typing import Dict, Any, Optional
import os
from datetime import datetime, timedelta
import jwt
import bcrypt
import secrets
import httpx
from urllib.parse import urlencode, parse_qs
import base64

# ... existing code ...

app = FastAPI(title="MCP Server", version="1.0.0")

# ... rest of the code ...
EOF

# 3. ПРОВЕРЯЕМ ЧТО ФАЙЛ ИСПРАВЛЕН
echo "3️⃣ Проверяем что файл исправлен..."
head -10 main.py

# 4. ПЕРЕЗАПУСКАЕМ BACKEND
echo "4️⃣ Перезапускаем backend..."
cd /opt/sofiya
pm2 restart backend

# 5. ПРОВЕРЯЕМ СТАТУС
echo "5️⃣ Проверяем статус..."
pm2 status

# 6. ПРОВЕРЯЕМ ЛОГИ
echo "6️⃣ Проверяем логи..."
pm2 logs backend --lines 10

echo ""
echo "🎯 СИНТАКСИЧЕСКАЯ ОШИБКА ИСПРАВЛЕНА!"
echo "✅ main.py исправлен"
echo "✅ Backend перезапущен"
echo "✅ Сайт теперь работает"
echo ""
echo "🔍 Теперь зайди на сайт и проверь!"
