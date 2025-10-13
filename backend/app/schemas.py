from pydantic import BaseModel, EmailStr
from typing import Optional, Any, Dict

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    is_active: bool
    
    class Config:
        from_attributes = True

class UserSettingsResponse(BaseModel):
    wordpress_url: Optional[str] = None
    wordpress_username: Optional[str] = None
    has_wordpress_credentials: bool
    has_wordstat_credentials: bool
    mcp_sse_url: Optional[str] = None
    mcp_connector_id: Optional[str] = None
    timezone: str = "UTC"
    language: str = "ru"
    
    class Config:
        from_attributes = True

class UserSettingsUpdate(BaseModel):
    wordpress_url: Optional[str] = None
    wordpress_username: Optional[str] = None
    wordpress_password: Optional[str] = None
    wordstat_client_id: Optional[str] = None
    wordstat_client_secret: Optional[str] = None
    wordstat_redirect_uri: Optional[str] = None
    mcp_sse_url: Optional[str] = None
    mcp_connector_id: Optional[str] = None
    timezone: Optional[str] = None
    language: Optional[str] = None

class MCPRequest(BaseModel):
    tool: str
    params: Dict[str, Any] = {}

class MCPResponse(BaseModel):
    success: bool
    result: Optional[Any] = None
    message: str
