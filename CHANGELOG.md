# Changelog

All notable changes to this project will be documented in this file.

## [2.0.0] - 2025-10-14

### 🚀 Direct Access Edition

Major release with direct MCP connector access, full JSON-RPC support, and enhanced user experience.

### ✨ New Features

#### Direct MCP Access
- **Direct Connector URLs**: Connect without OAuth using `https://mcp-kv.ru/mcp/sse/{connector_id}`
- **No Authorization Required**: Direct access for trusted connectors
- **JWT Token Support**: Long-lived tokens for persistent connections
- **Personal MCP Manifests**: User-specific manifests with pre-configured tokens

#### Enhanced JSON-RPC Support
- **Complete Protocol Implementation**: Full initialize, tools/list, tools/call support
- **Direct HTTP Responses**: ChatGPT-compatible response handling
- **25 Powerful Tools**: WordPress (15) + Yandex Wordstat (10) integration
- **Improved Error Handling**: Better diagnostics and user guidance

#### Technical Improvements
- **Fixed Syntax Errors**: Resolved tools array formatting issues
- **Enhanced Logging**: Better request/response tracking
- **Improved SSE**: Better Server-Sent Events handling
- **MCP Protocol Compliance**: Full adherence to MCP specifications

### 📚 Documentation
- **DIRECT_MCP_ACCESS.md**: Complete direct connection guide
- **Enhanced README**: Updated setup and usage instructions
- **Comprehensive CHANGELOG**: Detailed version history

### 🎯 Usage Options

#### Direct Connection (Recommended)
```
https://mcp-kv.ru/mcp/sse/{your-connector-id}
```

#### OAuth Connection
```
https://mcp-kv.ru/.well-known/mcp.json
```

### 🛠️ Available Tools
- **WordPress Management**: 15 tools for posts, pages, media, users, comments
- **Yandex Wordstat**: 10 tools for keyword research and analytics

### 🚀 Production Ready
This release is stable and ready for production use with ChatGPT, Make.com, and other MCP clients.

## [1.0.0] - 2025-10-14

### 🎉 First Stable Release

Full MCP (Model Context Protocol) Server with OAuth 2.0, ChatGPT integration, WordPress and Yandex Wordstat API support.

### ✨ Features

#### OAuth & Authentication
- **OAuth 2.0 Authorization Server** with full PKCE (S256) support
- **Dynamic Client Registration** (RFC 7591)
- **HTTP Basic Auth** for token endpoint
- **JWT authentication** for direct API access
- Multi-user support with isolated connectors

#### MCP Protocol
- **SSE (Server-Sent Events)** transport with endpoint discovery
- **JSON-RPC 2.0** message format
- Protocol version: `2025-03-26`
- Supports `initialize`, `tools/list`, and `tools/call` methods

#### WordPress Integration (18 tools)
- **Posts**: create, update, get, delete, search, bulk_update
- **Categories**: create, get, update, delete
- **Media**: upload, upload_from_url, get, delete
- **Comments**: create, get, update, delete

#### Yandex Wordstat Integration (7 tools)
- **User Info**: get account limits and remaining quota
- **Regions Tree**: get available regions for statistics
- **Top Requests**: get popular search queries
- **Dynamics**: get search query trends over time
- **Regions**: get geographic distribution of queries
- **Token Management**: set and validate API tokens
- **Auto Setup**: diagnostic and configuration wizard

### 🔐 Security

- **PKCE** (Proof Key for Code Exchange) with S256 challenge method
- **Per-user connector isolation** with unique identifiers
- **Encrypted credentials storage** in database
- **HTTPS** with Let's Encrypt certificates
- **Authorization header forwarding** through Nginx

### 🚀 Deployment

- **Nginx reverse proxy** configuration for HTTPS and routing
- **Systemd service** for automatic startup and management
- **Production-ready setup** with logging and monitoring
- **Environment variables** for configuration
- **Database migrations** with SQLAlchemy

### 🔧 Technical Stack

- **Backend**: Python 3.9+, FastAPI, SQLAlchemy, httpx
- **Frontend**: Next.js 14, TypeScript, Tailwind CSS
- **Database**: SQLite (production-ready with foreign keys)
- **Web Server**: Nginx 1.24.0
- **SSL**: Let's Encrypt (Certbot)
- **Platform**: Ubuntu 24.04 LTS

### 📚 API Endpoints

#### OAuth
- `GET /.well-known/oauth-authorization-server` - OAuth metadata
- `GET /.well-known/oauth-protected-resource` - Resource metadata
- `POST /oauth/register` - Dynamic client registration
- `GET /oauth/authorize` - Authorization endpoint
- `POST /oauth/authorize` - Authorization confirmation
- `POST /oauth/token` - Token exchange (supports JSON and form-encoded)

#### MCP
- `GET /.well-known/mcp.json` - MCP server manifest
- `GET /mcp/sse` - SSE connection (OAuth)
- `POST /mcp/sse` - JSON-RPC requests (OAuth)
- `GET /mcp/sse/{connector_id}` - SSE connection (JWT)
- `POST /mcp/sse/{connector_id}` - JSON-RPC requests (JWT)

#### Application
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `GET /user/me` - Current user info
- `GET /user/settings` - User settings
- `PUT /user/settings` - Update settings
- `GET /mcp/tools` - Available tools list

### 🐛 Bug Fixes

- Fixed OAuth token endpoint to support HTTP Basic Auth (ChatGPT compatibility)
- Fixed client_secret validation for public clients with PKCE
- Fixed JSON-RPC responses to return directly in HTTP POST (not through SSE)
- Fixed Nginx Authorization header forwarding
- Fixed Wordstat API endpoints to use correct v1 API
- Fixed SSE endpoint event format per MCP specification

### 📖 Documentation

- MCP server discovery via `.well-known/mcp.json`
- OAuth 2.0 flow with PKCE documentation
- Deployment guide for Ubuntu
- API documentation with examples
- Security best practices

### 🎯 ChatGPT Integration

Successfully tested and working with:
- ChatGPT Connectors (Developer Mode)
- Make.com MCP integration
- Custom OAuth applications

### 🔗 Links

- **Repository**: https://github.com/Horosheff/sofa
- **Server**: https://mcp-kv.ru
- **MCP Manifest**: https://mcp-kv.ru/.well-known/mcp.json

---

## How to Use

### For Users
1. Visit https://mcp-kv.ru and register
2. Configure WordPress and/or Wordstat API credentials
3. Copy your connector URL from settings
4. Add connector to ChatGPT or Make.com

### For Developers
1. Clone the repository
2. Set up environment variables
3. Run migrations: `python backend/init_db.py`
4. Start backend: `cd backend && uvicorn app.main:app --reload`
5. Start frontend: `cd frontend && npm run dev`

### For Server Deployment
1. Follow instructions in `DEPLOYMENT.md`
2. Configure Nginx with provided config
3. Set up SSL with Certbot
4. Configure systemd services
5. Update and restart services

---

**Full Changelog**: https://github.com/Horosheff/sofa/commits/v1.0.0

