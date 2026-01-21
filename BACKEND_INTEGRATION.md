# Backend Integration Documentation

## Overview

The ByteDent chatbot integrates with a Laravel backend (`senior-dental-backend`) that acts as the API gateway for web/mobile clients.

---

## Architecture

```
┌─────────────────┐
│  Web/Mobile     │
│  Frontend       │
└────────┬────────┘
         │ HTTPS
         ▼
┌──────────────────────────────────┐
│  Laravel Backend (PHP)           │
│  /opt/senior-dental-backend      │
│  Port: Unknown (likely 80/443)   │
│                                  │
│  ┌───────────────────────────┐  │
│  │  ChatController           │  │
│  │  - /v1/chat/message       │  │
│  │  - /v1/chat/history       │  │
│  │  - /v1/chat/health        │  │
│  └──────────┬────────────────┘  │
│             │                    │
│  ┌──────────▼────────────────┐  │
│  │  ChatService              │  │
│  │  - sendMessage()          │  │
│  │  - checkHealth()          │  │
│  │  - getHistory() [stub]    │  │
│  └──────────┬────────────────┘  │
└─────────────┼────────────────────┘
              │ HTTP
              ▼
┌──────────────────────────────────┐
│  ByteDent Chatbot (FastAPI)     │
│  /opt/senior-dental-ai-chatbot  │
│  Port: 8001 (localhost only)     │
│                                  │
│  POST /api/v1/chat               │
│  GET  /api/v1/health             │
│  GET  /api/v1/health/ready       │
└──────────────────────────────────┘
```

---

## Request Flow

### 1. Frontend → Laravel Backend

**Endpoint:** `POST /v1/chat/message`
**Authentication:** Bearer token (required)

**Request:**
```json
{
  "message": "What is a root canal?",
  "conversation_id": "optional-conv-id"
}
```

### 2. Laravel → Chatbot Service

**Endpoint:** `POST http://localhost:8001/api/v1/chat`

**Request:**
```json
{
  "message": "What is a root canal?",
  "conversation_id": "uuid-generated-or-provided",
  "metadata": {
    "user_id": 123,
    "source": "laravel_backend"
  }
}
```

**Headers:**
```
X-Request-ID: uuid
Content-Type: application/json
```

### 3. Chatbot → Laravel Response

**Chatbot Response:**
```json
{
  "type": "answer",
  "message": "Root canal treatment is...",
  "citations": ["...", "..."],
  "handoff_reason": null,
  "retrieval": {
    "top_similarity_score": 0.85,
    "chunks_retrieved": 5,
    "retrieval_time_ms": 25
  },
  "request_id": "uuid",
  "conversation_id": "uuid",
  "processing_time_ms": 450,
  "timestamp": "2026-01-21T..."
}
```

**Laravel Transforms To:**
```json
{
  "answer": "Root canal treatment is...",
  "type": "answer",
  "handoff_to_human": false,
  "handoff_reason": null,
  "citations": ["...", "..."],
  "confidence": 0.85,
  "conversation_id": "uuid",
  "request_id": "uuid",
  "processing_time_ms": 450
}
```

### 4. Laravel → Frontend Response

**Final Response:**
```json
{
  "success": true,
  "data": {
    "answer": "Root canal treatment is...",
    "type": "answer",
    "handoff_to_human": false,
    "handoff_reason": null,
    "citations": ["...", "..."],
    "confidence": 0.85,
    "conversation_id": "uuid",
    "request_id": "uuid",
    "processing_time_ms": 450
  }
}
```

---

## Important Integration Points

### 1. **Conversation ID Management**

- ✅ Laravel generates UUID if not provided by frontend
- ✅ Conversation ID passed to chatbot
- ❌ **NOT STORED** - No conversation history in database yet
- ⚠️  Each request is stateless (no memory of previous messages)

### 2. **Authentication & User Context**

- ✅ Frontend authenticates with Laravel (Bearer token)
- ✅ Laravel extracts `user_id` from auth session
- ✅ User ID passed to chatbot in `metadata`
- ❌ **NOT USED** - Chatbot doesn't currently use user_id for personalization

### 3. **Health Monitoring**

- ✅ Backend endpoint: `GET /v1/chat/health`
- ✅ Checks chatbot readiness: `GET http://localhost:8001/api/v1/health/ready`
- ✅ Cached for 30 seconds to avoid hammering service
- ✅ Returns HTTP 503 if chatbot unhealthy

### 4. **Error Handling**

Laravel provides fallback when chatbot fails:
```json
{
  "answer": "I apologize, but I am temporarily unavailable...",
  "type": "handoff",
  "handoff_to_human": true,
  "handoff_reason": "service_unavailable: ...",
  "error": true
}
```

### 5. **Configuration**

**Laravel `.env`:**
```bash
CHATBOT_SERVICE_URL=http://localhost:8001
CHATBOT_TIMEOUT=60  # seconds
```

---

## Current Limitations

| Feature | Status | Impact |
|---------|--------|--------|
| **Conversation History** | ❌ Not Implemented | Each query is independent |
| **User Personalization** | ❌ Not Used | No user-specific responses |
| **Message Storage** | ❌ No Database | Can't retrieve past conversations |
| **Multi-turn Context** | ❌ No Memory | Chatbot can't reference previous messages |
| **Session Management** | ⚠️  Minimal | Conversation ID exists but not leveraged |

---

## Proposed Enhancements

### Priority 1: Add Conversation History Storage

**Laravel Side:**
```php
// Migration: chat_messages table
- id
- user_id
- conversation_id
- message
- response
- type (answer/handoff)
- confidence
- created_at
```

**Chatbot Side:**
```python
# Accept conversation history in request
{
  "message": "current question",
  "conversation_id": "uuid",
  "history": [
    {"role": "user", "content": "previous question"},
    {"role": "assistant", "content": "previous answer"}
  ]
}
```

### Priority 2: Multi-turn Conversation Context

**Chatbot Enhancement:**
- Include last 5 messages in context window
- Re-rank retrieved chunks based on conversation flow
- Detect follow-up questions ("What about...?", "Can you explain more?")

### Priority 3: User-Specific Responses

**Use Cases:**
- Doctors vs Patients (adjust technical level)
- Language preference
- Previous interaction patterns

---

## Testing the Integration

### 1. Test Backend → Chatbot Connection

From Laravel backend server:
```bash
curl -X POST http://localhost:8001/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is CBCT?",
    "conversation_id": "test-123",
    "metadata": {"user_id": 1, "source": "test"}
  }'
```

### 2. Test Laravel API (requires auth token)

```bash
curl -X POST https://your-domain.com/api/v1/chat/message \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is a root canal?"
  }'
```

### 3. Test Health Check

```bash
curl https://your-domain.com/api/v1/chat/health
```

---

## Security Considerations

1. ✅ **Network Isolation**
   - Chatbot runs on localhost:8001 only
   - Not exposed to internet
   - Laravel acts as secure gateway

2. ✅ **Authentication**
   - Frontend must authenticate with Laravel
   - Chatbot trusts requests from Laravel

3. ⚠️  **Rate Limiting**
   - Laravel should implement rate limiting
   - Chatbot has basic rate limiting (60 req/min)

4. ⚠️  **Input Sanitization**
   - Laravel validates chat requests
   - Chatbot should also validate

---

## Monitoring Points

### Laravel Backend

**Log Location:** `/opt/senior-dental-backend/storage/logs/laravel.log`

**Key Events:**
- `Sending message to chatbot`
- `Chatbot response received`
- `Chatbot service connection failed`

### Chatbot Service

**Log Location:** `journalctl -u bytedent-chatbot`

**Key Events:**
- `POST /api/v1/chat` requests
- Processing times
- Error rates
- Health check results

---

## Known Issues

1. **404 Errors in Logs**
   ```
   POST /_next/server HTTP/1.1" 404
   POST /api HTTP/1.1" 404
   POST /app HTTP/1.1" 404
   ```
   **Cause:** Unknown client probing endpoints
   **Impact:** None (expected 404s)
   **Action:** Can safely ignore or add nginx rules to block

2. **No Conversation Persistence**
   **Cause:** Database schema not created yet
   **Impact:** Users can't see chat history
   **Action:** Implement chat_messages table

3. **No Session Timeout**
   **Cause:** Conversation IDs never expire
   **Impact:** Unlimited conversation growth (if implemented)
   **Action:** Add TTL to conversations

---

## Future Roadmap

### Phase 1: Basic History (Backend)
- [ ] Create chat_messages database table
- [ ] Store all user queries and responses
- [ ] Implement `getHistory()` method
- [ ] Add pagination for history retrieval

### Phase 2: Multi-turn Context (Chatbot)
- [ ] Accept conversation history in request
- [ ] Include last N messages in RAG context
- [ ] Detect follow-up questions
- [ ] Add conversation summarization

### Phase 3: Advanced Features
- [ ] User profiling (doctor vs patient responses)
- [ ] Conversation summarization
- [ ] Suggested follow-up questions
- [ ] Multi-language support
- [ ] Voice input/output integration

---

## Contact Points

**Backend Repository:** `/opt/senior-dental-backend` (Laravel PHP)
**Chatbot Repository:** `/opt/senior-dental-ai-chatbot` (FastAPI Python)
**Backend Service:** Laravel FPM + Nginx
**Chatbot Service:** systemd (bytedent-chatbot.service)

**Deployment:** Both services auto-deploy via GitHub Actions
