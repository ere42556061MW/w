# Bot Manager Web Server - API Documentation

## Overview
Comprehensive REST API for Bot Manager with authentication, bot management, real-time communication, and analytics.

---

## Table of Contents
1. [Authentication APIs](#authentication-apis)
2. [User Management APIs](#user-management-apis)
3. [Bot Management APIs](#bot-management-apis)
4. [Bot Operations APIs](#bot-operations-apis)
5. [Statistics & Analytics APIs](#statistics--analytics-apis)
6. [Data Export APIs](#data-export-apis)
7. [Logs & Messages APIs](#logs--messages-apis)
8. [Commands APIs](#commands-apis)
9. [Socket.IO Events](#socketio-events)

---

## Authentication APIs

### Register User
**POST** `/api/auth/register`

Register a new user account.

**Request Body:**
```json
{
  "username": "string",
  "email": "string",
  "password": "string (min 8 chars)",
  "fullname": "string (optional)"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Registration successful"
}
```

---

### Login User
**POST** `/api/auth/login`

Authenticate user and get session token.

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "success": true,
  "user": {
    "id": 1,
    "username": "string",
    "email": "string",
    "fullname": "string",
    "role": "user"
  }
}
```
*Sets `session_token` cookie (httponly, max 7 days)*

---

### Logout User
**POST** `/api/auth/logout`

Logout current user and invalidate session.

**Response:**
```json
{
  "success": true
}
```

---

### Get Current User
**GET** `/api/auth/me`

Get current authenticated user information.

**Response:**
```json
{
  "user": {
    "id": 1,
    "username": "string",
    "email": "string",
    "fullname": "string",
    "role": "user",
    "created_at": "ISO timestamp"
  }
}
```

---

### Update Profile
**POST** `/api/auth/update-profile`

Update user profile information.

**Request Body:**
```json
{
  "fullname": "string (optional)",
  "phone": "string (optional)",
  "birthday": "string (optional)",
  "gender": "string (optional)"
}
```

**Response:**
```json
{
  "success": true
}
```

---

### Change Password
**POST** `/api/auth/change-password`

Change user password.

**Request Body:**
```json
{
  "old_password": "string",
  "new_password": "string (min 8 chars)"
}
```

**Response:**
```json
{
  "success": true
}
```

---

### Forgot Password
**POST** `/api/auth/forgot-password`

Request password reset token.

**Request Body:**
```json
{
  "email": "string"
}
```

**Response:**
```json
{
  "success": true,
  "message": "If email exists, reset link has been sent"
}
```

---

### Reset Password
**POST** `/api/auth/reset-password`

Reset password using token.

**Request Body:**
```json
{
  "token": "string",
  "new_password": "string (min 8 chars)"
}
```

**Response:**
```json
{
  "success": true
}
```

---

### Delete Account
**POST** `/api/auth/delete-account`

Delete user account permanently.

**Request Body:**
```json
{
  "password": "string"
}
```

**Response:**
```json
{
  "success": true
}
```

---

## User Management APIs

### Get All Users (Admin)
**GET** `/api/users`

Get list of all users (admin only).

**Response:**
```json
{
  "users": [
    {
      "id": 1,
      "username": "string",
      "email": "string",
      "fullname": "string",
      "created_at": "ISO timestamp",
      "role": "user"
    }
  ],
  "count": 10
}
```

---

### Get User Details
**GET** `/api/users/<user_id>`

Get user profile (own or admin only).

**Response:**
```json
{
  "user": {
    "id": 1,
    "username": "string",
    "email": "string",
    "fullname": "string",
    "phone": "string",
    "birthday": "string",
    "gender": "string",
    "created_at": "ISO timestamp",
    "last_login": "ISO timestamp",
    "is_active": true,
    "role": "user"
  }
}
```

---

### Get User Bots
**GET** `/api/users/<user_id>/bots`

Get all bots owned by a user.

**Response:**
```json
{
  "bots": [
    {
      "id": "bot_id",
      "name": "string",
      "status": "online/offline",
      "created_at": "ISO timestamp",
      "owner_id": 1
    }
  ],
  "count": 5
}
```

---

### Search Users
**GET** `/api/users/search?q=<query>`

Search users by username or email (admin only).

**Query Parameters:**
- `q` (required): Search query (min 2 chars)

**Response:**
```json
{
  "users": [
    {
      "id": 1,
      "username": "string",
      "email": "string",
      "fullname": "string",
      "created_at": "ISO timestamp"
    }
  ],
  "count": 5
}
```

---

## Bot Management APIs

### Get My Bots
**GET** `/api/my-bots`

Get all bots owned by current user.

**Response:**
```json
{
  "bots": [
    {
      "id": "bot_id",
      "name": "string",
      "status": "online/offline",
      "created_at": "ISO timestamp",
      "metadata": {}
    }
  ],
  "count": 5
}
```

---

### Create Bot
**POST** `/api/my-bots`

Create a new bot.

**Request Body:**
```json
{
  "name": "string",
  "metadata": {} (optional)
}
```

**Response:**
```json
{
  "success": true,
  "bot_id": "string",
  "token": "string"
}
```

---

### Get Bot Details
**GET** `/api/my-bots/<bot_id>`

Get specific bot details.

**Response:**
```json
{
  "bot": {
    "id": "bot_id",
    "name": "string",
    "status": "online/offline",
    "created_at": "ISO timestamp",
    "last_active": "ISO timestamp",
    "metadata": {}
  }
}
```

---

### Update Bot
**PUT** `/api/my-bots/<bot_id>`

Update bot information.

**Request Body:**
```json
{
  "name": "string (optional)",
  "metadata": {} (optional)
}
```

**Response:**
```json
{
  "success": true
}
```

---

### Delete Bot
**DELETE** `/api/my-bots/<bot_id>`

Delete a bot.

**Response:**
```json
{
  "success": true
}
```

---

### Get Bot Token
**GET** `/api/my-bots/<bot_id>/token`

Get bot authentication token.

**Response:**
```json
{
  "token": "string"
}
```

---

### Regenerate Bot Token
**POST** `/api/my-bots/<bot_id>/regenerate-token`

Generate new bot authentication token.

**Response:**
```json
{
  "success": true,
  "token": "string"
}
```

---

### Get Bot Data
**GET** `/api/my-bots/<bot_id>/data`

Get stored bot data.

**Response:**
```json
{
  "data": null or {}
}
```

---

### Get All Bots (Admin)
**GET** `/api/admin/bots`

Get all bots in system (admin only).

**Response:**
```json
{
  "bots": [
    {
      "id": "bot_id",
      "name": "string",
      "status": "online/offline",
      "owner_id": 1,
      "created_at": "ISO timestamp"
    }
  ],
  "count": 20
}
```

---

### Get Bot Info
**GET** `/api/bot/<bot_id>/info`

Get detailed bot information with stats.

**Response:**
```json
{
  "bot": {
    "id": "bot_id",
    "name": "string",
    "status": "online/offline",
    "created_at": "ISO timestamp",
    "metadata": {}
  },
  "stats": {
    "total_commands": 100,
    "pending_commands": 5,
    "completed_commands": 90,
    "failed_commands": 5
  },
  "online": true
}
```

---

## Bot Operations APIs

### Send Command to Bot
**POST** `/api/bot/<bot_id>/send-command`

Send a command to bot for execution.

**Request Body:**
```json
{
  "type": "string (command type)",
  "payload": {} (optional)
}
```

**Response:**
```json
{
  "status": "ok",
  "command": {
    "id": "cmd_id",
    "bot_id": "bot_id",
    "type": "string",
    "payload": {},
    "status": "pending",
    "created_at": "ISO timestamp"
  }
}
```

---

### Restart Bot
**POST** `/api/bot/<bot_id>/restart`

Send restart command to bot.

**Response:**
```json
{
  "status": "ok",
  "command": { ... }
}
```

---

### Stop Bot
**POST** `/api/bot/<bot_id>/stop`

Send stop command to bot.

**Response:**
```json
{
  "status": "ok",
  "command": { ... }
}
```

---

### Get Bot Settings
**GET** `/api/bot/<bot_id>/settings`

Get bot configuration settings.

**Response:**
```json
{
  "settings": {}
}
```

---

### Update Bot Settings
**PUT** `/api/bot/<bot_id>/settings`

Update bot settings.

**Request Body:**
```json
{
  "key": "value",
  ...
}
```

**Response:**
```json
{
  "success": true,
  "settings": {}
}
```

---

### Get Bot Commands History
**GET** `/api/bot/<bot_id>/commands-history?limit=50`

Get command execution history.

**Query Parameters:**
- `limit`: Number of records (default: 50)

**Response:**
```json
{
  "commands": [
    {
      "id": "cmd_id",
      "type": "string",
      "status": "completed",
      "created_at": "ISO timestamp",
      "completed_at": "ISO timestamp",
      "result": {}
    }
  ],
  "count": 50
}
```

---

## Statistics & Analytics APIs

### Get Overview Stats
**GET** `/api/stats/overview`

Get system-wide statistics overview.

**Response:**
```json
{
  "total_users": 10,
  "total_bots": 25,
  "user_bots": 5,
  "total_commands": 1000,
  "pending_commands": 5,
  "total_logs": 5000,
  "total_messages": 2000,
  "connected_clients": 10
}
```

---

### Get Bot Statistics
**GET** `/api/stats/bot/<bot_id>`

Get detailed bot statistics.

**Response:**
```json
{
  "total_commands": 100,
  "pending_commands": 5,
  "completed_commands": 90,
  "failed_commands": 5,
  "total_logs": 500,
  "total_messages": 200,
  "command_types": {
    "send_message": 80,
    "restart": 10,
    "stop": 10
  }
}
```

---

## Data Export APIs

### Export Logs
**GET** `/api/export/logs?bot_id=<bot_id>&limit=1000`

Export logs as JSON.

**Query Parameters:**
- `bot_id` (optional): Filter by bot
- `limit`: Number of records (default: 1000)

**Response:**
```json
{
  "exported_at": "ISO timestamp",
  "count": 500,
  "logs": [
    {
      "type": "string",
      "message": "string",
      "timestamp": "ISO timestamp",
      "metadata": {},
      "bot_id": "bot_id"
    }
  ]
}
```

---

### Export Messages
**GET** `/api/export/messages?bot_id=<bot_id>&limit=1000`

Export messages as JSON.

**Query Parameters:**
- `bot_id` (optional): Filter by bot
- `limit`: Number of records (default: 1000)

**Response:**
```json
{
  "exported_at": "ISO timestamp",
  "count": 200,
  "messages": [
    {
      "bot_id": "bot_id",
      "message": "string",
      "author_id": "string",
      "author_name": "string",
      "thread_id": "string",
      "thread_type": "GROUP",
      "timestamp": "ISO timestamp",
      "metadata": {}
    }
  ]
}
```

---

### Export Bot Data
**GET** `/api/export/bot-data/<bot_id>`

Export complete bot data including logs and messages.

**Response:**
```json
{
  "exported_at": "ISO timestamp",
  "bot": { ... },
  "data": { ... },
  "commands": [ ... ],
  "logs": [ ... ],
  "messages": [ ... ]
}
```

---

## Logs & Messages APIs

### Get All Logs
**GET** `/api/logs?limit=100`

Get system logs.

**Query Parameters:**
- `limit`: Number of records (default: 100)

**Response:**
```json
{
  "logs": [ ... ],
  "count": 100
}
```

---

### Post Bot Logs
**POST** `/api/bot/<bot_id>/logs`

Bot sends logs to server.

**Request Body:**
```json
{
  "type": "info/error/warning",
  "message": "string",
  "metadata": {} (optional)
}
```
or array of logs.

**Response:**
```json
{
  "status": "ok",
  "received": 1
}
```

---

### Get Messages
**GET** `/api/messages?limit=100`

Get system messages.

**Query Parameters:**
- `limit`: Number of records (default: 100)

**Response:**
```json
{
  "messages": [ ... ],
  "count": 100
}
```

---

### Post Bot Messages
**POST** `/api/bot/<bot_id>/messages`

Bot sends message events to server.

**Request Body:**
```json
{
  "message": "string",
  "author_id": "string",
  "author_name": "string",
  "thread_id": "string",
  "thread_type": "GROUP/USER",
  "metadata": {} (optional)
}
```

**Response:**
```json
{
  "status": "ok"
}
```

---

### Sync Bot Data
**POST** `/api/bot/<bot_id>/sync`

Bot syncs data (friends, groups, etc.) to server.

**Request Body:**
```json
{
  "groups": [ ... ],
  "friends": [ ... ],
  "metadata": {} (optional)
}
```

**Response:**
```json
{
  "status": "ok"
}
```

---

### Get Bot Data
**GET** `/api/bot/<bot_id>/data`

Get stored bot data.

**Response:**
```json
{
  "data": { ... },
  "source": "database/memory",
  "updated_at": "ISO timestamp"
}
```

---

## Commands APIs

### List Commands
**GET** `/api/commands?bot_id=<bot_id>`

List all commands.

**Query Parameters:**
- `bot_id` (optional): Filter by bot

**Response:**
```json
{
  "commands": [ ... ],
  "count": 100
}
```

---

### Create Command
**POST** `/api/commands`

Create a new command for bot.

**Request Body:**
```json
{
  "bot_id": "string",
  "type": "string",
  "payload": {} (optional)
}
```

**Response:**
```json
{
  "status": "queued",
  "command": { ... }
}
```

---

### Get Pending Commands
**GET** `/api/bot/<bot_id>/commands?limit=10`

Get pending commands for bot.

**Query Parameters:**
- `limit`: Number of commands (default: 10)

**Response:**
```json
{
  "commands": [ ... ],
  "count": 5
}
```

---

### Acknowledge Command
**POST** `/api/commands/<command_id>/ack`

Mark command as completed.

**Request Body:**
```json
{
  "status": "completed/failed",
  "result": {} (optional)
}
```

**Response:**
```json
{
  "status": "ok",
  "command": { ... }
}
```

---

## Socket.IO Events

### Client Events (From Frontend)

#### Connect
Establishes WebSocket connection.

**Event:** `connect`

#### Disconnect
Closes WebSocket connection.

**Event:** `disconnect`

#### Send Message
Send message via bot.

**Event:** `send_message`

**Data:**
```json
{
  "bot_id": "string",
  "thread_id": "string",
  "thread_type": "GROUP/USER",
  "message": "string",
  "attachments": [] (optional),
  "metadata": {} (optional)
}
```

### Server Events (To Frontend)

#### Connection Established
Server confirms connection.

**Event:** `connection_established`

**Data:**
```json
{
  "status": "connected",
  "client_id": "string",
  "timestamp": "ISO timestamp"
}
```

#### New Log
New log entry received.

**Event:** `new_log`

**Data:**
```json
{
  "type": "string",
  "message": "string",
  "timestamp": "ISO timestamp",
  "metadata": {},
  "bot_id": "string"
}
```

#### New Message
New message received.

**Event:** `new_message`

**Data:**
```json
{
  "bot_id": "string",
  "message": "string",
  "author_id": "string",
  "author_name": "string",
  "thread_id": "string",
  "thread_type": "string",
  "timestamp": "ISO timestamp"
}
```

#### Bot Update
Bot status change.

**Event:** `bot_update`

**Data:**
```json
{
  "action": "register/status_update",
  "bot_id": "string",
  "status": "online/offline",
  "data": {}
}
```

#### Command Update
Command status change.

**Event:** `command_update`

**Data:**
```json
{
  "id": "cmd_id",
  "status": "pending/completed/failed",
  "result": {},
  "completed_at": "ISO timestamp"
}
```

#### Message Sent
Message queued for sending.

**Event:** `message_sent`

**Data:**
```json
{
  "status": "queued/error",
  "command_id": "string",
  "timestamp": "ISO timestamp"
}
```

#### Bot Data Sync
Bot data synchronized.

**Event:** `bot_data_sync`

**Data:**
```json
{
  "bot_id": "string",
  "data": {}
}
```

---

## Error Responses

All endpoints return appropriate HTTP status codes:

- **200**: Success
- **400**: Bad request
- **401**: Unauthorized/Invalid credentials
- **403**: Forbidden (access denied)
- **404**: Not found
- **500**: Server error

Error response format:
```json
{
  "error": "Error message"
}
```

---

## Authentication

Most endpoints require authentication via session cookie. 

To authenticate:
1. POST to `/api/auth/login` with credentials
2. Server sets `session_token` cookie (httponly)
3. Include cookie in subsequent requests

Admin-only endpoints require `role: 'admin'`.

---

## Rate Limiting

Currently no rate limiting. Recommended for production:
- Implement rate limiting per IP/user
- Use Flask-Limiter or similar

---

## Environment

Base URL: `http://localhost:5000`

In production, update:
- `SECRET_KEY` in Flask config
- Socket.IO CORS settings
- Database path
- Port number

---

## Version

API Version: 1.0
Last Updated: December 2024
