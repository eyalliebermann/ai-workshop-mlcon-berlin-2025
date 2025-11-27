# Conversational AI System - Multi-Agent POC

## Purpose
Playground for solution architects to experiment with patterns, protocols, and frameworks for conversational AI systems. Current implementation: Berlin sober scene assistant with conversation memory.

## Development Philosophy
Lean Agile development in short cycles by a single engineer. Each should prodocce a **working demo**. Complexity is kept at minimum and is always serving the features demonstrated. 

**Core principle:** Start simple, introduce complexity only when needed. Commit to protocols, not stacks. 

## Roadmap

### Development Stages
1. ✅ Single Assistant, no conversation memory - REST chat protocol established
2. ✅ Single agent with conversation memory - REST session protocol established
3. Single agent + inline tools integration
4. Single agent + MCP tools integration
5. ⏭️ Server-sent events (SSE) for streaming responses
6. Multi-agent orchestration
13. Agent-to-agent communication (A2A) protocol
multi agent delegation


11. Introduce monitoring dashboards
12. Introduce guardrails for safety
7. Web component integration for embeddability
8. Add authentication layer
9. Deploy to public cloud
10. Add persistent session database
14. WebSocket migration + voice support
15. Open to multiple users
16. Monitor for security and compliance
17. Connect with personal information based on user token

### Stack Rationale

**Backend: Python + FastAPI**
Python's AI ecosystem is unmatched. FastAPI provides async capabilities and SSE support. LangGraph (later stages) is Python-native.

**Frontend: Svelte** (planned)
Compiles to vanilla JavaScript with no runtime. Critical for web component embeddability in third-party sites. Current implementation uses plain HTML/JS.

---

## Getting Started

### Prerequisites
- Python 3.12 for maximal compatibility
- OpenAI API key
- Modern web browser - e.g. Chrome/ Safari

### Quick Start

**1. Backend Setup**

```bash
cd backend
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
uv sync
```

**2. Validate Backend**

```bash
# Run tests first
uv run pytest test_main.py -v

# All tests should pass before proceeding
# Test specification in test_main.py defines behavioral requirements
```

**3. Start Backend**

```bash
uv run uvicorn main:app --reload --port 8002
```

API Documentation: http://127.0.0.1:8002/docs

**4. Test Backend Endpoints**

```bash
# Create session
curl -X POST http://127.0.0.1:8002/session

# Chat with session
curl -X POST http://127.0.0.1:8002/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What sober events are in Berlin?", "session_id": "YOUR_SESSION_ID"}'

# Chat without session (backward compatible)
curl -X POST http://127.0.0.1:8002/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Tell me about Berlin sober scene"}'
```

**5. Start Frontend**

```bash
# Option 1: Direct file open
open frontend/index.html

# Option 2: HTTP server (recommended)
cd frontend
python -m http.server 8080
# Open http://localhost:8080
```

**6. Test Full System**

- Frontend should auto-create a session on load
- Send messages and verify conversation memory works
- Refresh page - new session created, previous conversation lost (expected with in-memory storage)

---

## Current Implementation

### Status: Stage 1 Complete ✅

**Working Features:**
- REST API with FastAPI
- Session management (in-memory)
- Conversation memory across multiple turns
- OpenAI GPT-4o-mini integration
- System prompt defines assistant personality
- CORS enabled for frontend integration
- Comprehensive test suite with behavioral specifications

**API Endpoints:**

```
POST /session              → Create new session, returns session_id
POST /chat                 → Send message (with optional session_id)
```

**Protocol:**

```javascript
// Create session
POST /session
Response: {"session_id": "uuid-v4"}

// Chat with memory
POST /chat
Request:  {"message": "...", "session_id": "uuid"}
Response: {"response": "..."}

// Chat without memory (backward compatible)
POST /chat
Request:  {"message": "..."}
Response: {"response": "..."}
```

### Backend Architecture

**Structure:**
```
backend/
├── main.py              # FastAPI app, session management, OpenAI integration
├── test_main.py         # Test suite with behavioral specifications
├── pyproject.toml       # uv dependencies
├── .env.example         # Environment template
└── .env                 # Your API keys (gitignored)
```

**Key Implementation Details:**

*Session Storage:* In-memory dictionary mapping session IDs to conversation history. Each session contains: system prompt + all user/assistant message pairs. Sessions are ephemeral (lost on restart).

*Conversation Flow:*
1. User sends message with session_id
2. Backend appends user message to session history
3. Full history sent to OpenAI API
4. Assistant response appended to session history
5. Response returned to user

*System Prompt:* Defines assistant as Berlin sober scene expert. Focuses on alcohol-free events, wellness activities, conscious community. See `SYSTEM_PROMPT` in `main.py`.

*Testing:* Test specification at top of `test_main.py` defines 7 core behavioral requirements. Tests validate behavior, not implementation details.

### Frontend Architecture

**Structure:**
```
frontend/
└── index.html          # Complete chat UI (HTML + CSS + JS in single file)
```

**Implementation:** Plain HTML/JS with modern gradient UI. No build step required.

**Features:**
- Auto-creates session on page load
- Sends session_id with all messages
- Real-time message display
- Loading indicators and error handling
- Keyboard shortcuts (Enter to send)
- Auto-scrolling chat

**Configuration:**
Backend URL set in JavaScript: `const API_URL = 'http://127.0.0.1:8002/chat'`

---

## Next: Prioritized User Stories

### High Priority

**US-1: Streaming Responses with SSE**
*As a user, I want to see the assistant's response appear word-by-word in real-time*
- Implement SSE endpoint for message streaming
- Update frontend to consume SSE stream
- Maintain backward compatibility with REST

**US-2: Persistent Session Storage**
*As a user, I want my conversations to survive server restarts*
- Replace in-memory sessions with Redis or SQLite
- Add session expiration (e.g., 24 hours)
- Add session retrieval endpoint

**US-3: Conversation History UI**
*As a user, I want to see my full conversation history on page load*
- Add `GET /session/{id}/history` endpoint
- Frontend loads and displays previous messages
- Handle long conversations (pagination or infinite scroll)

### Medium Priority

**US-4: System Prompt Configuration**
*As a developer, I want to customize the assistant's personality without code changes*
- Move system prompt to configuration file or environment variable
- Add prompt template support for dynamic context injection
- Document prompt engineering best practices

**US-5: Rate Limiting and Usage Tracking**
*As an operator, I want to prevent abuse and track API usage*
- Implement rate limiting per session/IP
- Add usage metrics (message count, token usage)
- Add simple admin dashboard

**US-6: Multi-Session Management**
*As a user, I want to manage multiple conversation threads*
- Add session naming/description
- List all user sessions
- Delete/archive sessions

### Low Priority

**US-7: Tool Integration - Web Search**
*As a user, I want current event information from the web*
- Add inline tool for web search
- Assistant can search for current Berlin events
- Display sources in UI

**US-8: Export Conversations**
*As a user, I want to export my chat history*
- Add export endpoint (JSON, markdown, PDF)
- Frontend download button
- Privacy controls

**US-9: Migrate to Svelte + Web Components**
*As a developer, I want a maintainable, embeddable frontend*
- Rewrite frontend in Svelte
- Build as web component
- Maintain API compatibility

---

## Protocol Evolution Plan

Current protocol (REST) is intentionally simple. Future protocols maintain backward compatibility:

**Stage 2 (SSE):**
```
POST /session/{id}/message → Returns SSE stream
Events: message_delta, tool_call, tool_result, error, done
```

**Stage 5 (WebSocket):**
```
WS /session/{id}/stream
Same event schema as SSE + binary frames for audio
```

Each protocol layer is designed to migrate forward without breaking existing clients.
