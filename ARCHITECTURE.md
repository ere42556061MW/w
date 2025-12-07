# Bot Manager API - Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      CLIENT APPLICATIONS                        │
│  (Web, Mobile, Desktop, Bot Clients)                            │
└────────────┬────────────────────────────────────────┬──────────┘
             │                                        │
             │ HTTP/REST                             │ WebSocket
             │                                        │
┌────────────▼────────────────────────────────────────▼──────────┐
│                    FLASK WEB SERVER                             │
│                  (web_server.py on Port 5000)                  │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │         AUTHENTICATION & SESSION MANAGEMENT             │   │
│  │  - Login/Register                                       │   │
│  │  - Session tokens (cookie-based)                        │   │
│  │  - Password reset                                       │   │
│  │  - Role-based access control                            │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              API ENDPOINTS (54 total)                   │   │
│  ├─────────────────────────────────────────────────────────┤   │
│  │ • Authentication (9)     ▸ Login, Register, Password    │   │
│  │ • User Management (4)    ▸ List, Search, Details       │   │
│  │ • Bot Management (9)     ▸ CRUD, Tokens, Info          │   │
│  │ • Bot Operations (5)     ▸ Restart, Stop, Settings      │   │
│  │ • Statistics (2)         ▸ Overview, Per-Bot Stats      │   │
│  │ • Data Export (3)        ▸ Logs, Messages, Bot Data     │   │
│  │ • Logs & Messages (6)    ▸ Get, Post, Sync             │   │
│  │ • Commands (4)           ▸ Create, List, Acknowledge    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │         REAL-TIME COMMUNICATION (Socket.IO)             │   │
│  │  - Live command updates                                 │   │
│  │  - Message/Log streaming                                │   │
│  │  - Bot status changes                                   │   │
│  │  - Connected client management                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
└────────────┬────────────────────────────────────────┬──────────┘
             │                                        │
             │ Database Access                        │ In-Memory Storage
             │                                        │
┌────────────▼──────────────────┐   ┌─────────────────▼──────────┐
│    SQLite Database             │   │  In-Memory Data Stores     │
│  (data/users.db)              │   │                            │
├─────────────────────────────┤   ├──────────────────────────────┤
│ • users                      │   │ • logs_storage (500 max)    │
│ • sessions                   │   │ • messages_storage (500)    │
│ • password_resets            │   │ • commands (200 per bot)    │
│ • bots                       │   │ • bot_instances            │
│ • bot_tokens                 │   │ • bot_data_store           │
│ • bot auth & ownership       │   │ • connected_clients        │
│                              │   │                            │
│ (Persistent)                 │   │ (Volatile)                 │
└──────────────────────────────┘   └──────────────────────────────┘
```

---

## API Request Flow

```
┌──────────────┐
│   CLIENT     │
└──────┬───────┘
       │
       ▼ HTTP Request
┌────────────────────────────────────────┐
│  FLASK ROUTING LAYER                   │
│  (Route matching & HTTP method)        │
└────────────┬───────────────────────────┘
             │
             ▼
┌────────────────────────────────────────┐
│  AUTHENTICATION MIDDLEWARE             │
│  (Check session token, validate user)  │
└────────────┬───────────────────────────┘
             │
             ▼
┌────────────────────────────────────────┐
│  AUTHORIZATION CHECK                   │
│  (Verify permissions/ownership)        │
└────────────┬───────────────────────────┘
             │
             ▼
┌────────────────────────────────────────┐
│  INPUT VALIDATION                      │
│  (Sanitize and validate request data)  │
└────────────┬───────────────────────────┘
             │
             ▼
┌────────────────────────────────────────┐
│  BUSINESS LOGIC                        │
│  (Process request, update data)        │
└────────────┬───────────────────────────┘
             │
             ▼
┌────────────────────────────────────────┐
│  DATA PERSISTENCE                      │
│  (Save to DB or in-memory store)       │
└────────────┬───────────────────────────┘
             │
             ▼
┌────────────────────────────────────────┐
│  EVENT EMISSION                        │
│  (Emit Socket.IO events to clients)    │
└────────────┬───────────────────────────┘
             │
             ▼
┌────────────────────────────────────────┐
│  RESPONSE GENERATION                   │
│  (Format JSON response)                │
└────────────┬───────────────────────────┘
             │
             ▼ HTTP Response
┌──────────────┐
│   CLIENT     │
└──────────────┘
```

---

## Authentication & Authorization Hierarchy

```
┌─────────────────────────────────────────┐
│         UNAUTHENTICATED (Public)        │
├─────────────────────────────────────────┤
│ • GET  /api/health                      │
│ • POST /api/auth/register               │
│ • POST /api/auth/login                  │
│ • POST /api/auth/forgot-password        │
│ • POST /api/auth/reset-password         │
│ • POST /api/bot/auth                    │
│ • POST /api/bots/register               │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│      AUTHENTICATED (Login Required)     │
├─────────────────────────────────────────┤
│ • GET  /api/auth/me                     │
│ • POST /api/auth/logout                 │
│ • POST /api/auth/change-password        │
│ • POST /api/auth/delete-account         │
│ • All user endpoints                    │
│ • All my-bots endpoints                 │
│ • Stats & export (filtered by user)     │
└─────────────────────────────────────────┘
          │                    │
    (Regular User)      (Admin User)
          │                    │
          ▼                    ▼
┌──────────────────┐  ┌───────────────────┐
│ Can access own:  │  │ Can access:       │
│ • Profile        │  │ • All users       │
│ • Bots           │  │ • All bots        │
│ • Commands       │  │ • Admin endpoints │
│ • Data           │  │ • User search     │
│                  │  │ • System stats    │
└──────────────────┘  └───────────────────┘
```

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    BOT CLIENT (Running)                     │
│  (Bot instance using SDK or direct API calls)              │
└────────────────────┬────────────────────────────────────────┘
                     │
      ┌──────────────┴──────────────┐
      │ 1. Register Bot             │
      │ 2. Get Pending Commands     │
      │ 3. Report Status            │
      │ 4. Send Logs/Messages       │
      │ 5. Sync Data                │
      │
      ▼
┌─────────────────────────────────────────────────────────────┐
│                  BOT MANAGER SERVER                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────────────────────┐                      │
│  │ Bot Status Management            │                      │
│  │ • Track online/offline status    │                      │
│  │ • Store last_active timestamp    │                      │
│  │ • Keep metadata                  │                      │
│  └──────────────────────────────────┘                      │
│                  │                                          │
│                  ▼                                          │
│  ┌──────────────────────────────────┐                      │
│  │ Command Queue System              │                      │
│  │ • Pending commands per bot        │                      │
│  │ • Execution tracking              │                      │
│  │ • Result storage                  │                      │
│  └──────────────────────────────────┘                      │
│                  │                                          │
│                  ▼                                          │
│  ┌──────────────────────────────────┐                      │
│  │ Logging & Analytics               │                      │
│  │ • In-memory log storage           │                      │
│  │ • Message tracking                │                      │
│  │ • Command history                 │                      │
│  └──────────────────────────────────┘                      │
│                  │                                          │
│                  ▼                                          │
│  ┌──────────────────────────────────┐                      │
│  │ Data Persistence                  │                      │
│  │ • SQLite database                 │                      │
│  │ • Bot definitions                 │                      │
│  │ • User accounts                   │                      │
│  │ • Tokens & sessions               │                      │
│  └──────────────────────────────────┘                      │
│                                                             │
└────────────────┬────────────────────────────────────────────┘
                 │
      ┌──────────┴──────────┐
      │ Emits Socket.IO     │
      │ Events to Clients   │
      │
      ▼
┌─────────────────────────────────────────────────────────────┐
│              FRONTEND/WEB CLIENT                            │
│  (Dashboard, Admin Panel, Bot Control)                      │
│                                                             │
│  • Real-time updates via WebSocket                         │
│  • REST API for data operations                            │
│  • User-friendly interface                                 │
│  • Analytics & dashboards                                  │
└─────────────────────────────────────────────────────────────┘
```

---

## Command Lifecycle

```
CLIENT                          SERVER                          BOT
  │                              │                              │
  │──1. POST /bot/<id>/cmd ───► │                              │
  │                              │                              │
  │◄─2. Response (queued) ─────── │                              │
  │                              │                              │
  │                       ┌─────────────────┐                   │
  │                       │ Command queued  │                   │
  │                       │ Status: pending │                   │
  │                       └─────────────────┘                   │
  │                              │                              │
  │                   ┌──────────►│                              │
  │                   │3. Socket.IO emit   │                    │
  │                   │new_command event   │                    │
  │                              │                              │
  │                              │──4. GET /commands ────────► │
  │                              │                              │
  │                              │◄─ Returns pending commands ─ │
  │                              │                              │
  │                              │ 5. Bot executes command      │
  │                              │    ............................
  │                              │                   ◄────────┘
  │                              │                              │
  │                       ┌─────────────────────┐               │
  │                       │ 6. POST /ack        │               │
  │                       │ Command completed   │               │
  │◄──────────────────── │ Status: completed ──┤ ───────────► │
  │                       └─────────────────────┘               │
  │                              │                              │
  │◄─7. Socket.IO emit ─────────│                              │
  │   command_update event      │                              │
  │                              │                              │
```

---

## Database Schema Relationships

```
┌──────────────────┐
│     USERS        │
├──────────────────┤
│ id (PK)          │
│ username         │
│ email            │
│ password_hash    │
│ fullname         │
│ role             │
│ created_at       │
│ last_login       │
└────────┬─────────┘
         │ (1:N)
         │
         ├─────────────────────────────┐
         │                             │
         ▼                             ▼
    ┌─────────────┐           ┌──────────────────┐
    │  SESSIONS   │           │      BOTS        │
    ├─────────────┤           ├──────────────────┤
    │ id (PK)     │           │ id (PK)          │
    │ user_id (FK)│           │ user_id (FK)     │
    │ token       │           │ name             │
    │ expires_at  │           │ status           │
    │ created_at  │           │ bot_data         │
    └─────────────┘           │ created_at       │
                              │ last_active      │
         │ (1:N)              │ metadata         │
         │                    └──────┬───────────┘
    ┌────────────────┐              │ (1:N)
    │ PASSWORD_RESETS│              │
    ├────────────────┤              ▼
    │ id (PK)        │        ┌──────────────────┐
    │ user_id (FK)   │        │   BOT_TOKENS     │
    │ token          │        ├──────────────────┤
    │ expires_at     │        │ id (PK)          │
    │ used           │        │ bot_id (FK)      │
    │ created_at     │        │ token            │
    └────────────────┘        │ created_at       │
                              │ last_used        │
                              └──────────────────┘
```

---

## API Performance Characteristics

```
Operation Type          │ Complexity │ Performance │ Notes
────────────────────────┼────────────┼─────────────┼──────────────────
Login/Authentication    │ O(1)       │ Fast        │ Hash lookup
Get User Profile        │ O(1)       │ Fast        │ Direct DB query
List Users (Admin)      │ O(n)       │ Fast        │ DB query, <1000 users
Search Users            │ O(n)       │ Fast        │ DB LIKE query
Get User Bots           │ O(1)       │ Fast        │ DB FK query
Get Bot Info            │ O(1)       │ Fast        │ DB + in-memory merge
Send Command            │ O(log n)   │ Fast        │ Queue insert
List Commands           │ O(k)       │ Fast        │ k=command limit
Get Stats Overview      │ O(1)       │ Fast        │ Counter queries
Get Bot Stats           │ O(m)       │ Fair        │ m=log items
Export Data             │ O(m+k)    │ Fair        │ m=logs, k=commands
Socket.IO Emit          │ O(c)       │ Fair        │ c=connected clients
```

---

## Error Handling Flow

```
┌──────────────┐
│ Request      │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────┐
│ Authentication Check         │
├──────────────────────────────┤
│ ✓ Valid token?               │
└───────┬──────────────────────┘
        │
   ┌────┴────┐
   │          │
  No         Yes
   │          │
   ▼          ▼
┌─────────┐  ┌──────────────────────────────┐
│ 401/403 │  │ Authorization Check          │
│ Error   │  ├──────────────────────────────┤
└─────────┘  │ ✓ Has permission?            │
             └───────┬──────────────────────┘
                     │
                ┌────┴────┐
                │          │
              No          Yes
                │          │
                ▼          ▼
            ┌─────────┐  ┌──────────────────────────────┐
            │ 403/403 │  │ Input Validation             │
            │ Error   │  ├──────────────────────────────┤
            └─────────┘  │ ✓ Valid parameters?          │
                         └───────┬──────────────────────┘
                                 │
                            ┌────┴────┐
                            │          │
                          No          Yes
                            │          │
                            ▼          ▼
                        ┌─────────┐  ┌──────────────────────────────┐
                        │400 Error│  │ Business Logic               │
                        └─────────┘  ├──────────────────────────────┤
                                     │ ✓ Logic success?             │
                                     └───────┬──────────────────────┘
                                             │
                                        ┌────┴────┐
                                        │          │
                                      No          Yes
                                        │          │
                                        ▼          ▼
                                    ┌─────────┐  ┌──────────────────────────────┐
                                    │400/500  │  │ 200 Success Response         │
                                    │Error    │  ├──────────────────────────────┤
                                    └─────────┘  │ Return JSON with data        │
                                                 └──────────────────────────────┘
```

---

## Scalability Considerations

### Current Limitations
```
┌─────────────────────────┬──────────┐
│ Component               │ Limit    │
├─────────────────────────┼──────────┤
│ In-memory logs          │ 500      │
│ In-memory messages      │ 500      │
│ Commands per bot        │ 200      │
│ Connected clients       │ Unlimited│
│ Database records        │ Unlimited│
│ Command queue (pending) │ Unlimited│
└─────────────────────────┴──────────┘
```

### Recommendations for Production
```
For 1,000+ concurrent users:
├─ Move logs/messages to database
├─ Implement Redis caching layer
├─ Use connection pooling
├─ Add database indexing
├─ Implement rate limiting
├─ Use load balancing (nginx)
├─ Separate read/write databases
├─ Archive old logs periodically
└─ Monitor performance metrics

For 10,000+ concurrent users:
├─ Implement microservices
├─ Use message queue (RabbitMQ/Kafka)
├─ Separate bot management service
├─ Implement caching clusters
├─ Use CDN for static files
├─ Database sharding
├─ Implement API gateway
└─ Advanced monitoring & alerting
```

---

## Integration Points

```
┌─────────────────────────────────────────────────┐
│          BOT MANAGER SYSTEM                      │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌──────────────────────────────────────────┐  │
│  │ Integrates With:                         │  │
│  ├──────────────────────────────────────────┤  │
│  │ • Bot Frameworks (pymessenger, etc)      │  │
│  │ • External APIs (webhooks)               │  │
│  │ • Databases (SQLite, MySQL, etc)        │  │
│  │ • Cache Stores (Redis)                   │  │
│  │ • Message Queues (RabbitMQ)              │  │
│  │ • Analytics (custom or external)         │  │
│  │ • Monitoring (Prometheus, DataDog)       │  │
│  │ • Authentication (OAuth, LDAP)           │  │
│  └──────────────────────────────────────────┘  │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

**Created:** December 2024
**Architecture Version:** 1.1
**Status:** Ready for Production (with recommendations)
