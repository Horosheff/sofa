"""
Админ панель API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from typing import Optional, List
import json

from .database import get_db
from .auth import get_current_admin_user
from .models import User, UserSettings, ActivityLog, AdminLog, LoginAttempt

router = APIRouter(prefix="/admin", tags=["admin"])

def log_admin_action(
    db: Session,
    admin_user: User,
    action_type: str,
    action_description: str,
    target_user_id: Optional[int] = None,
    changes: Optional[dict] = None,
    request: Optional[Request] = None
):
    """Логирование действий администратора"""
    log = AdminLog(
        admin_user_id=admin_user.id,
        action_type=action_type,
        action_description=action_description,
        target_user_id=target_user_id,
        changes=json.dumps(changes) if changes else None,
        ip_address=request.client.host if request else None,
        user_agent=request.headers.get("user-agent") if request else None
    )
    db.add(log)
    db.commit()

@router.get("/dashboard")
async def get_admin_dashboard(
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Получить данные для админ дашборда"""
    
    # Статистика пользователей
    total_users = db.query(func.count(User.id)).scalar() or 0
    active_users = db.query(func.count(User.id)).filter(User.is_active == True).scalar() or 0
    
    # Новые пользователи за неделю
    week_ago = datetime.utcnow() - timedelta(days=7)
    new_users_week = db.query(func.count(User.id)).filter(
        User.created_at >= week_ago
    ).scalar() or 0
    
    # Общая активность
    total_actions = db.query(func.count(ActivityLog.id)).scalar() or 0
    
    # Активность за последние 24 часа
    day_ago = datetime.utcnow() - timedelta(days=1)
    actions_today = db.query(func.count(ActivityLog.id)).filter(
        ActivityLog.created_at >= day_ago
    ).scalar() or 0
    
    # Топ активных пользователей
    top_users = db.query(
        User.id,
        User.email,
        User.full_name,
        func.count(ActivityLog.id).label('action_count')
    ).join(ActivityLog, User.id == ActivityLog.user_id).group_by(
        User.id
    ).order_by(desc('action_count')).limit(10).all()
    
    top_users_list = [
        {
            "id": user_id,
            "email": email,
            "full_name": full_name,
            "action_count": action_count
        }
        for user_id, email, full_name, action_count in top_users
    ]
    
    # Статистика по типам действий
    actions_by_type = db.query(
        ActivityLog.action_type,
        func.count(ActivityLog.id).label('count')
    ).group_by(ActivityLog.action_type).all()
    
    actions_stats = {action_type: count for action_type, count in actions_by_type}
    
    # Активность по дням за последние 30 дней
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    daily_activity = db.query(
        func.date(ActivityLog.created_at).label('date'),
        func.count(ActivityLog.id).label('count')
    ).filter(
        ActivityLog.created_at >= thirty_days_ago
    ).group_by(func.date(ActivityLog.created_at)).all()
    
    daily_activity_list = [
        {"date": str(date), "count": count}
        for date, count in daily_activity
    ]
    
    # Статистика ошибок
    error_count = db.query(func.count(ActivityLog.id)).filter(
        ActivityLog.status == 'error'
    ).scalar() or 0
    
    return {
        "users": {
            "total": total_users,
            "active": active_users,
            "new_week": new_users_week
        },
        "activity": {
            "total": total_actions,
            "today": actions_today,
            "errors": error_count
        },
        "top_users": top_users_list,
        "actions_by_type": actions_stats,
        "daily_activity": daily_activity_list
    }

@router.get("/users")
async def get_all_users(
    skip: int = 0,
    limit: int = 50,
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Получить список всех пользователей с фильтрами"""
    
    query = db.query(User)
    
    if search:
        query = query.filter(
            (User.email.contains(search)) | (User.full_name.contains(search))
        )
    
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    total = query.count()
    users = query.order_by(desc(User.created_at)).offset(skip).limit(limit).all()
    
    users_list = [
        {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "is_admin": user.is_admin,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None
        }
        for user in users
    ]
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "users": users_list
    }

@router.get("/users/{user_id}")
async def get_user_details(
    user_id: int,
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Получить детальную информацию о пользователе"""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    # Настройки
    settings = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
    
    # Статистика активности
    total_actions = db.query(func.count(ActivityLog.id)).filter(
        ActivityLog.user_id == user_id
    ).scalar() or 0
    
    # Последние действия
    recent_activities = db.query(ActivityLog).filter(
        ActivityLog.user_id == user_id
    ).order_by(desc(ActivityLog.created_at)).limit(20).all()
    
    activities_list = [
        {
            "id": activity.id,
            "action_type": activity.action_type,
            "action_name": activity.action_name,
            "status": activity.status,
            "created_at": activity.created_at.isoformat() if activity.created_at else None
        }
        for activity in recent_activities
    ]
    
    return {
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "is_admin": user.is_admin,
            "created_at": user.created_at.isoformat() if user.created_at else None
        },
        "settings": {
            "has_wordpress": bool(settings and settings.wordpress_url),
            "has_wordstat": bool(settings and settings.wordstat_client_id),
            "mcp_connector_id": settings.mcp_connector_id if settings else None
        } if settings else None,
        "activity": {
            "total_actions": total_actions,
            "recent_activities": activities_list
        }
    }

@router.put("/users/{user_id}/block")
async def block_user(
    user_id: int,
    request: Request,
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Заблокировать пользователя"""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    if user.is_admin:
        raise HTTPException(status_code=403, detail="Нельзя заблокировать администратора")
    
    user.is_active = False
    db.commit()
    
    # Логируем действие
    log_admin_action(
        db=db,
        admin_user=admin_user,
        action_type="user_block",
        action_description=f"Заблокирован пользователь {user.email}",
        target_user_id=user_id,
        request=request
    )
    
    return {"message": f"Пользователь {user.email} заблокирован"}

@router.put("/users/{user_id}/unblock")
async def unblock_user(
    user_id: int,
    request: Request,
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Разблокировать пользователя"""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    user.is_active = True
    db.commit()
    
    # Логируем действие
    log_admin_action(
        db=db,
        admin_user=admin_user,
        action_type="user_unblock",
        action_description=f"Разблокирован пользователь {user.email}",
        target_user_id=user_id,
        request=request
    )
    
    return {"message": f"Пользователь {user.email} разблокирован"}

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    request: Request,
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Удалить пользователя"""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    if user.is_admin:
        raise HTTPException(status_code=403, detail="Нельзя удалить администратора")
    
    user_email = user.email
    
    # Удаляем связанные данные
    db.query(UserSettings).filter(UserSettings.user_id == user_id).delete()
    db.query(ActivityLog).filter(ActivityLog.user_id == user_id).delete()
    db.delete(user)
    db.commit()
    
    # Логируем действие
    log_admin_action(
        db=db,
        admin_user=admin_user,
        action_type="user_delete",
        action_description=f"Удалён пользователь {user_email}",
        target_user_id=user_id,
        request=request
    )
    
    return {"message": f"Пользователь {user_email} удалён"}

@router.get("/logs")
async def get_activity_logs(
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,
    action_type: Optional[str] = None,
    status: Optional[str] = None,
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Получить логи активности с фильтрами"""
    
    query = db.query(ActivityLog)
    
    if user_id:
        query = query.filter(ActivityLog.user_id == user_id)
    
    if action_type:
        query = query.filter(ActivityLog.action_type == action_type)
    
    if status:
        query = query.filter(ActivityLog.status == status)
    
    total = query.count()
    logs = query.order_by(desc(ActivityLog.created_at)).offset(skip).limit(limit).all()
    
    logs_list = [
        {
            "id": log.id,
            "user_id": log.user_id,
            "action_type": log.action_type,
            "action_name": log.action_name,
            "status": log.status,
            "details": log.details,
            "error_message": log.error_message,
            "ip_address": log.ip_address,
            "created_at": log.created_at.isoformat() if log.created_at else None
        }
        for log in logs
    ]
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "logs": logs_list
    }

@router.get("/admin-logs")
async def get_admin_logs(
    skip: int = 0,
    limit: int = 50,
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Получить логи действий администраторов"""
    
    query = db.query(AdminLog)
    
    total = query.count()
    logs = query.order_by(desc(AdminLog.created_at)).offset(skip).limit(limit).all()
    
    logs_list = [
        {
            "id": log.id,
            "admin_user_id": log.admin_user_id,
            "action_type": log.action_type,
            "action_description": log.action_description,
            "target_user_id": log.target_user_id,
            "changes": json.loads(log.changes) if log.changes else None,
            "ip_address": log.ip_address,
            "created_at": log.created_at.isoformat() if log.created_at else None
        }
        for log in logs
    ]
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "logs": logs_list
    }

@router.get("/stats")
async def get_platform_stats(
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Получить общую статистику платформы"""
    
    # Статистика пользователей
    total_users = db.query(func.count(User.id)).scalar() or 0
    active_users = db.query(func.count(User.id)).filter(User.is_active == True).scalar() or 0
    admin_users = db.query(func.count(User.id)).filter(User.is_admin == True).scalar() or 0
    
    # Статистика активности
    total_actions = db.query(func.count(ActivityLog.id)).scalar() or 0
    
    # По типам
    wordpress_actions = db.query(func.count(ActivityLog.id)).filter(
        ActivityLog.action_type == 'wordpress'
    ).scalar() or 0
    
    wordstat_actions = db.query(func.count(ActivityLog.id)).filter(
        ActivityLog.action_type == 'wordstat'
    ).scalar() or 0
    
    # Ошибки
    total_errors = db.query(func.count(ActivityLog.id)).filter(
        ActivityLog.status == 'error'
    ).scalar() or 0
    
    # Попытки входа
    total_login_attempts = db.query(func.count(LoginAttempt.id)).scalar() or 0
    failed_logins = db.query(func.count(LoginAttempt.id)).filter(
        LoginAttempt.success == False
    ).scalar() or 0
    
    return {
        "users": {
            "total": total_users,
            "active": active_users,
            "admins": admin_users
        },
        "activity": {
            "total": total_actions,
            "wordpress": wordpress_actions,
            "wordstat": wordstat_actions,
            "errors": total_errors
        },
        "security": {
            "total_login_attempts": total_login_attempts,
            "failed_logins": failed_logins
        }
    }

