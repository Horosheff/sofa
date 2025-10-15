#!/bin/bash
# 🧪 Тест Telegram инструментов через curl

CONNECTOR_ID="user-uJ6N73B10icXNuefggjLP9WQJ3ZNejEH"
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJtci5ydXRyYUBnbWFpbC5jb20iLCJleHAiOjE3NjA2NTY3NDd9.csAwciZat4lqKgzMXN8Maw9s36ulA4tB4VHL2CKm0TI"

echo "1️⃣ Тест: получить список инструментов (tools/list)"
curl -s -X POST "https://mcp-kv.ru/mcp/sse/$CONNECTOR_ID" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list"
  }' | jq '.result.tools | length'

echo ""
echo "2️⃣ Тест: вызвать telegram_get_bot_info"
curl -s -X POST "https://mcp-kv.ru/mcp/sse/$CONNECTOR_ID" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "telegram_get_bot_info",
      "arguments": {}
    }
  }' | jq '.'

echo ""
echo "3️⃣ Тест: вызвать wordpress_get_posts"
curl -s -X POST "https://mcp-kv.ru/mcp/sse/$CONNECTOR_ID" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
      "name": "wordpress_get_posts",
      "arguments": {}
    }
  }' | jq '.result.content[0].text' -r

echo ""
echo "✅ ГОТОВО!"

