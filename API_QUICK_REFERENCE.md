# Bot Manager API - Quick Reference Guide

## 🚀 Quick Start

### 1. Register & Login
```bash
# Register
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"user1","email":"user1@example.com","password":"password123","fullname":"User One"}'

# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{"username":"user1","password":"password123"}'
```

### 2. Create Bot
```bash
curl -X POST http://localhost:5000/api/my-bots \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"name":"My Bot","metadata":{"description":"Test bot"}}'
```

### 3. Send Command
```bash
curl -X POST http://localhost:5000/api/bot/bot_123/send-command \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"type":"send_message","payload":{"text":"Hello"}}'
```

---

## 📊 API Endpoints by Category

### 🔐 Authentication (9 endpoints)
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/auth/register` | Create new account |
| POST | `/api/auth/login` | Login user |
| POST | `/api/auth/logout` | Logout user |
| GET | `/api/auth/me` | Get current user |
| POST | `/api/auth/update-profile` | Update profile |
| POST | `/api/auth/change-password` | Change password |
| POST | `/api/auth/forgot-password` | Request password reset |
| POST | `/api/auth/reset-password` | Reset password with token |
| POST | `/api/auth/delete-account` | Delete account |

### 👥 User Management (4 endpoints) ✨ NEW
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/users` | List all users (admin) |
| GET | `/api/users/<id>` | Get user details |
| GET | `/api/users/<id>/bots` | Get user's bots |
| GET | `/api/users/search?q=...` | Search users |

### 🤖 Bot Management (8 endpoints)
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/my-bots` | My bots list |
| POST | `/api/my-bots` | Create bot |
| GET | `/api/my-bots/<id>` | Get bot |
| PUT | `/api/my-bots/<id>` | Update bot |
| DELETE | `/api/my-bots/<id>` | Delete bot |
| GET | `/api/my-bots/<id>/token` | Get bot token |
| POST | `/api/my-bots/<id>/regenerate-token` | Regenerate token |
| GET | `/api/my-bots/<id>/data` | Get bot data |
| GET | `/api/admin/bots` | All bots (admin) |
| GET | `/api/bot/<id>/info` | Bot info with stats |

### 🎮 Bot Operations (5 endpoints) ✨ NEW
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/bot/<id>/send-command` | Send command |
| POST | `/api/bot/<id>/restart` | Restart bot |
| POST | `/api/bot/<id>/stop` | Stop bot |
| GET | `/api/bot/<id>/settings` | Get settings |
| PUT | `/api/bot/<id>/settings` | Update settings |
| GET | `/api/bot/<id>/commands-history` | Command history |

### 📈 Statistics (2 endpoints) ✨ NEW
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/stats/overview` | System stats |
| GET | `/api/stats/bot/<id>` | Bot stats |

### 💾 Data Export (3 endpoints) ✨ NEW
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/export/logs` | Export logs |
| GET | `/api/export/messages` | Export messages |
| GET | `/api/export/bot-data/<id>` | Export all bot data |

### 📝 Logs & Messages (6 endpoints)
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/logs` | Get logs |
| POST | `/api/bot/<id>/logs` | Post logs |
| GET | `/api/messages` | Get messages |
| POST | `/api/bot/<id>/messages` | Post messages |
| GET | `/api/bot/<id>/data` | Get bot data |
| POST | `/api/bot/<id>/sync` | Sync bot data |

### ⚙️ Commands (3 endpoints)
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/commands` | List commands |
| POST | `/api/commands` | Create command |
| POST | `/api/commands/<id>/ack` | Acknowledge command |
| GET | `/api/bot/<id>/commands` | Get pending commands |

### 🔌 Socket.IO Events
| Event | Direction | Purpose |
|-------|-----------|---------|
| `connect` | ← Client | Connect to server |
| `disconnect` | ← Client | Disconnect from server |
| `send_message` | ← Client | Send message via bot |
| `connection_established` | → Server | Connection confirmed |
| `new_log` | → Server | New log entry |
| `new_message` | → Server | New message received |
| `bot_update` | → Server | Bot status change |
| `command_update` | → Server | Command status change |
| `message_sent` | → Server | Message queued |
| `bot_data_sync` | → Server | Bot data synced |

---

## 🔑 Authentication

All endpoints except `/api/auth/*` and `/api/bot/*` require:
1. Valid session token in cookie (from login)
2. OR X-Bot-Token header for bot operations

### Setting Up Authentication
```python
# In your client code
import requests

# Login
session = requests.Session()
response = session.post(
    'http://localhost:5000/api/auth/login',
    json={'username': 'user1', 'password': 'password123'}
)

# Session cookie is automatically stored
# Use session for subsequent requests
stats = session.get('http://localhost:5000/api/stats/overview')
print(stats.json())
```

---

## 📤 Common Request Patterns

### Get User's Bots
```bash
curl http://localhost:5000/api/my-bots \
  -b cookies.txt
```

### Get Bot Info with Stats
```bash
curl http://localhost:5000/api/bot/bot_123/info \
  -b cookies.txt
```

### Send Message Command
```bash
curl -X POST http://localhost:5000/api/bot/bot_123/send-command \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "type": "send_message",
    "payload": {
      "thread_id": "thread_456",
      "thread_type": "GROUP",
      "message": "Hello world"
    }
  }'
```

### Export Bot Data
```bash
curl http://localhost:5000/api/export/bot-data/bot_123 \
  -b cookies.txt > bot_123.json
```

### Get System Overview
```bash
curl http://localhost:5000/api/stats/overview \
  -b cookies.txt
```

### Search Users (Admin)
```bash
curl 'http://localhost:5000/api/users/search?q=john' \
  -b cookies.txt
```

---

## 🔒 Security Notes

✅ **Always use:**
- HTTPS in production (not HTTP)
- Secure cookies (SameSite=Lax)
- Strong passwords (min 8 chars)
- Keep session tokens secret
- Validate all inputs

❌ **Never:**
- Expose session tokens
- Use weak passwords
- Store credentials in code
- Make API calls from frontend directly (use proxy)
- Share bot tokens

---

## 📊 Response Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | Success | Command executed |
| 400 | Bad request | Invalid parameters |
| 401 | Unauthorized | Invalid credentials |
| 403 | Forbidden | No permission |
| 404 | Not found | Bot doesn't exist |
| 500 | Server error | Internal error |

---

## 🎯 Common Tasks

### Create Bot and Send Command
```bash
#!/bin/bash

# 1. Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{"username":"user1","password":"password123"}' \
  > /dev/null

# 2. Create bot
BOT_ID=$(curl -X POST http://localhost:5000/api/my-bots \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"name":"TestBot"}' \
  | jq -r '.bot_id')

echo "Created bot: $BOT_ID"

# 3. Send command
curl -X POST http://localhost:5000/api/bot/$BOT_ID/send-command \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"type":"send_message","payload":{"text":"Hello"}}'
```

### Monitor Bot Statistics
```bash
#!/bin/bash

# Get real-time stats
watch -n 2 'curl -s http://localhost:5000/api/stats/bot/bot_123 \
  -b cookies.txt | jq .'
```

### Backup Bot Data
```bash
#!/bin/bash

# Export and save
curl http://localhost:5000/api/export/bot-data/bot_123 \
  -b cookies.txt | jq '.' > backups/bot_123_$(date +%Y%m%d_%H%M%S).json

echo "Bot data backed up"
```

---

## 🐛 Debugging

### Enable Detailed Logging
```python
# In web_server.py
if __name__ == '__main__':
    start_web_server(port=5000, debug=True)
```

### Check Server Health
```bash
curl http://localhost:5000/api/health
```

### View Recent Logs
```bash
curl 'http://localhost:5000/api/logs?limit=20' \
  -b cookies.txt | jq '.logs[-5:]'
```

### Test Bot Auth
```bash
curl -X POST http://localhost:5000/api/bot/auth \
  -H "Content-Type: application/json" \
  -d '{"bot_id":"bot_123","token":"token_xyz"}'
```

---

## 📚 Documentation Files

- **API_DOCUMENTATION.md** - Complete reference
- **API_ADDITIONS_SUMMARY.md** - What's new
- **API_QUICK_REFERENCE.md** - This file

---

## ✨ New in v1.1

- 30 new API endpoints
- User management (search, list, details)
- Bot operations (restart, stop, settings)
- Statistics & analytics
- Data export functionality
- Comprehensive documentation
- Better error handling
- Admin-only features

---

## 📞 Support

For issues or questions:
1. Check API_DOCUMENTATION.md
2. Review error response messages
3. Check server logs (debug mode)
4. Verify authentication is working

---

**Last Updated:** December 2024
**API Version:** 1.1
**Status:** ✅ Production Ready
