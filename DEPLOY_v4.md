# 🚀 Deployment Guide - Version 4.0.0

## 📋 Pre-deployment Checklist

### 1. Server Requirements
- [x] Ubuntu 20.04+ / Debian 11+
- [x] Python 3.9+
- [x] Node.js 18+
- [x] Nginx
- [x] PM2
- [x] Git
- [x] SSL certificates (Let's Encrypt)

### 2. Backup
```bash
# Backup database
cp /var/www/sofa/backend/app.db /var/www/sofa/backups/app_v3_$(date +%Y%m%d).db

# Backup current version
cd /var/www/sofa
tar -czf ../sofa_v3_backup_$(date +%Y%m%d).tar.gz .
```

---

## 🔧 Deployment Steps

### Step 1: Update Code from GitHub

```bash
# Navigate to project
cd /var/www/sofa

# Stash any local changes
git stash

# Fetch latest
git fetch origin

# Checkout v4 tag
git checkout v4.0.0

# Or use main branch
# git pull origin main
```

### Step 2: Backend Update

```bash
cd /var/www/sofa/backend

# Activate venv
source venv/bin/activate

# Update dependencies
pip install -r requirements.txt

# Verify new modules
python -c "from app.helpers import is_valid_url; print('✓ Helpers OK')"
python -c "from app.mcp_handlers import SseManager; print('✓ MCP Handlers OK')"
python -c "from app.wordpress_tools import handle_wordpress_tool; print('✓ WP Tools OK')"
python -c "from app.wordstat_tools import handle_wordstat_tool; print('✓ WS Tools OK')"

# Run tests
python test_modules.py
```

### Step 3: Frontend Update

```bash
cd /var/www/sofa/frontend

# Install dependencies
npm install

# Build production
npm run build

# Check build
ls -lh .next/
```

### Step 4: Restart Services

```bash
# Restart backend (PM2)
pm2 restart mcp-backend

# Restart frontend (PM2)
pm2 restart mcp-frontend

# Check status
pm2 status
pm2 logs mcp-backend --lines 50
pm2 logs mcp-frontend --lines 50
```

### Step 5: Nginx

```bash
# Test nginx config
sudo nginx -t

# Reload nginx (if config changed)
sudo systemctl reload nginx

# Check status
sudo systemctl status nginx
```

---

## 🧪 Post-deployment Testing

### 1. Backend Health Check
```bash
# Test backend API
curl https://mcp-kv.ru/health

# Test MCP endpoint
curl https://mcp-kv.ru/api/health

# Check logs
pm2 logs mcp-backend --lines 100
```

### 2. Frontend Check
```bash
# Test frontend
curl -I https://mcp-kv.ru

# Check in browser
# https://mcp-kv.ru
```

### 3. Database Check
```bash
cd /var/www/sofa/backend
source venv/bin/activate

python -c "
from app.database import SessionLocal
from app.models import User
db = SessionLocal()
count = db.query(User).count()
print(f'Users in DB: {count}')
db.close()
"
```

### 4. MCP Tools Check
```bash
# Login to dashboard
# Navigate to Инструменты
# Verify 25 tools visible (18 WP + 7 WS)
```

---

## 🔍 Monitoring

### Check PM2 Status
```bash
pm2 status
pm2 monit
```

### View Logs
```bash
# Backend logs
pm2 logs mcp-backend --lines 100

# Frontend logs
pm2 logs mcp-frontend --lines 100

# Filter errors
pm2 logs mcp-backend --err --lines 50
```

### Check System Resources
```bash
# Memory usage
free -h

# Disk usage
df -h

# CPU usage
top -bn1 | head -20
```

---

## 🐛 Troubleshooting

### Issue: Backend won't start

**Symptoms:**
```
pm2 logs mcp-backend shows errors
```

**Solutions:**
```bash
cd /var/www/sofa/backend

# Check Python version
python --version  # Should be 3.9+

# Check venv
source venv/bin/activate
which python

# Test imports
python -c "import app.main"

# Check for missing dependencies
pip install -r requirements.txt

# Restart
pm2 restart mcp-backend
```

### Issue: Frontend won't build

**Symptoms:**
```
npm run build fails
```

**Solutions:**
```bash
cd /var/www/sofa/frontend

# Clear cache
rm -rf .next node_modules

# Reinstall
npm install

# Build
npm run build

# Check Node version
node --version  # Should be 18+
```

### Issue: 502 Bad Gateway

**Symptoms:**
```
Nginx shows 502 error
```

**Solutions:**
```bash
# Check if services are running
pm2 status

# Restart services
pm2 restart all

# Check nginx config
sudo nginx -t

# Check nginx logs
sudo tail -f /var/log/nginx/error.log
```

### Issue: Database locked

**Symptoms:**
```
sqlite3.OperationalError: database is locked
```

**Solutions:**
```bash
cd /var/www/sofa/backend

# Stop all processes
pm2 stop mcp-backend

# Check for locks
lsof app.db

# Restart
pm2 start mcp-backend
```

---

## 🔄 Rollback (if needed)

### Quick Rollback to v3

```bash
cd /var/www/sofa

# Stop services
pm2 stop all

# Checkout previous version
git checkout v3.0.0

# Restore database (if needed)
cp /var/www/sofa/backups/app_v3_20251015.db backend/app.db

# Restart services
pm2 restart all
```

---

## 📊 Performance Tuning

### PM2 Configuration

Create/update `ecosystem.config.js`:
```javascript
module.exports = {
  apps: [
    {
      name: 'mcp-backend',
      cwd: '/var/www/sofa/backend',
      script: 'venv/bin/uvicorn',
      args: 'app.main:app --host 0.0.0.0 --port 8000 --workers 4',
      instances: 1,
      exec_mode: 'fork',
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      env: {
        NODE_ENV: 'production'
      }
    },
    {
      name: 'mcp-frontend',
      cwd: '/var/www/sofa/frontend',
      script: 'npm',
      args: 'start',
      instances: 1,
      exec_mode: 'fork',
      autorestart: true,
      watch: false,
      max_memory_restart: '300M',
      env: {
        NODE_ENV: 'production',
        PORT: 3000
      }
    }
  ]
};
```

Apply:
```bash
cd /var/www/sofa
pm2 delete all
pm2 start ecosystem.config.js
pm2 save
```

---

## 🔐 Security Checklist

- [ ] SSL certificates valid
- [ ] Firewall configured (UFW)
- [ ] SSH keys only (no password auth)
- [ ] Nginx security headers enabled
- [ ] Rate limiting configured
- [ ] Database backups automated
- [ ] Logs rotated
- [ ] Secret keys in environment variables

---

## 📝 Environment Variables

Make sure these are set in `/var/www/sofa/backend/.env`:

```env
DATABASE_URL=sqlite:///./app.db
SECRET_KEY=your-production-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
MCP_SERVER_URL=https://mcp-kv.ru
FRONTEND_URL=https://mcp-kv.ru

# Yandex OAuth
YANDEX_CLIENT_ID=your-client-id
YANDEX_CLIENT_SECRET=your-client-secret
```

---

## 📈 Monitoring Commands

### Quick Health Check
```bash
#!/bin/bash
echo "=== PM2 Status ==="
pm2 status

echo -e "\n=== Backend Health ==="
curl -s https://mcp-kv.ru/health | jq

echo -e "\n=== Frontend Health ==="
curl -I https://mcp-kv.ru 2>&1 | head -1

echo -e "\n=== Disk Usage ==="
df -h | grep -E '(Filesystem|/dev/)'

echo -e "\n=== Memory Usage ==="
free -h

echo -e "\n=== Recent Errors ==="
pm2 logs --err --lines 5 --nostream
```

Save as `/var/www/sofa/health_check.sh` and run:
```bash
chmod +x /var/www/sofa/health_check.sh
/var/www/sofa/health_check.sh
```

---

## ✅ Deployment Complete!

After successful deployment, verify:

1. ✅ Backend responds on https://mcp-kv.ru/health
2. ✅ Frontend loads on https://mcp-kv.ru
3. ✅ Login works
4. ✅ Dashboard shows 25 tools
5. ✅ WordPress settings work
6. ✅ Wordstat settings work
7. ✅ No errors in PM2 logs
8. ✅ SSL certificate valid

---

## 📞 Support

If you encounter issues:

1. Check PM2 logs: `pm2 logs --lines 100`
2. Check nginx logs: `sudo tail -f /var/log/nginx/error.log`
3. Review this guide's troubleshooting section
4. Check GitHub Issues

---

**Version:** 4.0.0  
**Last Updated:** 2025-10-15  
**Status:** ✅ Production Ready

