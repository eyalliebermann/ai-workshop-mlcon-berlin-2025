# Corporate Website Assistant - Multi-Agent POC

## Purpose
Playground for solution architects to experiment with patterns, protocols, and frameworks for conversational AI systems. Uses a corporate website assistant as the reference scenario.

## Why This POC
Validate production patterns at increasing complexity:

1. Frontend/backend contract for real-time conversation
2. Agent-LLM integration and prompt management
3. Tool calling (inline, then MCP)
4. Real-time bidirectional communication and voice
5. Multi-agent orchestration and routing
6. Agent-to-agent communication (A2A)

## Development Approach
Agile and lean. Each stage ends with a **working demo**. Complexity increases incrementally. We do not build stage N+1 infrastructure until stage N works end-to-end.

**Core principle:** Start simple, introduce complexity only when needed. Commit to protocols, not stacks.

### Stages
1. Single agent, no tools - establish FE/BE contract via REST + SSE
2. Single agent + inline tools
3. Single agent + MCP tools
4. WebSocket migration + voice
5. Two agents + orchestrator
6. Multiple agents + A2A

---

## Stack

### Backend: Python + FastAPI

Python is the natural choice for AI workloads - richer ecosystem, more examples, better library support. FastAPI provides async capabilities and built-in SSE support. LangGraph (when introduced in later stages) is Python-native with mature documentation.

### Frontend: Svelte

Svelte compiles to vanilla JavaScript with no runtime overhead. This matters because the chat UI must eventually be embeddable as a web component in third-party websites. React and Vue ship their runtimes; Svelte compiles away. First-class web component support via `customElement: true`.

For professional appearance: Skeleton UI or shadcn-svelte.

---

## Frontend/Backend Protocol

### Requirements
- Stream agent responses in real-time (text deltas, tool calls, status)
- Support tool display instructions from agent to frontend
- Accept session context from frontend (user state, page context)
- Authentication-ready
- Extensible to voice without full rewrite

### Approach: REST + SSE, then WebSocket

Stages 1-3 use REST for requests and SSE for streaming responses. This is simple, standard, and sufficient for text-based interaction. The event schema is designed to port directly to WebSocket when stage 4 introduces voice and true bidirectional communication.

### Initial REST Endpoints
```
POST /session              → Initialize session, authenticate, return session ID
POST /session/{id}/message → Send user message, returns SSE stream
```

Additional endpoints (context retrieval, history, etc.) will be defined as stages demand them.

### SSE Event Schema
```
event: message_delta
data: {"content": "...", "role": "assistant"}

event: tool_call
data: {"tool": "...", "args": {...}, "display_hint": "..."}

event: tool_result
data: {"tool": "...", "result": {...}}

event: error
data: {"code": "...", "message": "..."}

event: done
data: {}
```

This schema transfers unchanged to WebSocket in stage 4, with added binary frames for audio.

---

## Backend Architecture

### Approach: Monolith First, Decompose Later

The backend starts as a single deployable unit containing:
- Protocol handling (REST/SSE, later WebSocket)
- Session management and auth
- Orchestrator logic
- Agent implementation(s)

Internal interfaces between these components are kept clean from the start. This allows extraction into separate services when complexity warrants it - external tools via MCP, external agents via A2A - without rewriting the core.

The stable contract with the frontend is the protocol layer (REST/SSE/WebSocket). Internally, orchestrator-to-agent and agent-to-tool interfaces follow the same principle: define the contract, swap implementations freely.

---

## Current Implementation Status

### Stage 0.5: Basic Chat (Completed)

We have a working end-to-end chat with OpenAI integration, but without sessions or streaming.

**What's Working:**
- FastAPI backend with OpenAI GPT-4o-mini
- HTML/JS frontend with modern UI
- Single-turn conversations (no history)
- CORS enabled
- Error handling

**Current Protocol:**
```
POST /chat
Request:  {"message": "..."}
Response: {"response": "..."}
```

This is simpler than the target Stage 1 protocol. Next step: add session management and conversation history.

---

## Implementation Details

### Backend

**Stack:** FastAPI + OpenAI GPT-4o-mini

#### Setup

```bash
cd backend
cp .env.example .env
# Add your OPENAI_API_KEY to .env
uv sync
```

#### Run

```bash
cd backend
uv run uvicorn main:app --reload --port 8002
```

#### Test

```bash
cd backend
uv run pytest test_main.py -v
```

#### API

```bash
curl -X POST http://127.0.0.1:8002/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What sober events are in Berlin?"}'
```

API Docs: http://127.0.0.1:8002/docs

#### Structure

```
backend/
├── main.py          # FastAPI app + OpenAI integration
├── test_main.py     # pytest suite
├── pyproject.toml   # uv dependencies
└── .env             # API keys
```

### Frontend

**Stack:** Plain HTML + JavaScript (no build step)

#### Run

```bash
# Simply open in browser
open frontend/index.html

# Or serve via HTTP server
cd frontend
python -m http.server 8080
# Then open http://localhost:8080
```

#### Features

- Modern gradient UI design
- Real-time message display
- Loading indicators
- Error handling with user feedback
- Keyboard support (Enter to send)
- Auto-scrolling chat area
- Responsive layout

#### Structure

```
frontend/
└── index.html       # Complete chat UI (HTML + CSS + JS)
```

#### Configuration

The frontend connects to the backend via:
```javascript
const API_URL = 'http://127.0.0.1:8002/chat';
```

Change this URL if running the backend on a different host/port.

---

## Next: Upgrade to Stage 1

**Goal:** Add session management and conversation history (REST, not yet SSE).

### Protocol Design

#### Session Management

```
POST /session
Response: {"session_id": "uuid-v4"}
```

Creates a new session and returns a unique identifier. The frontend stores this ID and includes it in subsequent requests.

#### Chat with History

```
POST /chat
Request:  {"session_id": "uuid", "message": "..."}
Response: {"response": "..."}
```

Backend maintains conversation history per session. Each message includes the full context of previous messages in that session.

#### Session Storage

**Implementation:** In-memory dictionary
```python
sessions = {
    "session-uuid-1": [
        {"role": "system", "content": "..."},
        {"role": "user", "content": "..."},
        {"role": "assistant", "content": "..."}
    ]
}
```

**Note:** This is ephemeral. Sessions are lost on server restart. For production, use Redis or a database.

#### Frontend Changes

1. On page load: `POST /session` → store `session_id`
2. On send message: Include `session_id` in request
3. Messages accumulate in conversation history

### Implementation Plan

- [ ] Add session creation endpoint
- [ ] Add in-memory session storage
- [ ] Update chat endpoint to accept session_id
- [ ] Store conversation history per session
- [ ] Update frontend to request session on load
- [ ] Update frontend to send session_id with messages
- [ ] Test multi-turn conversations

After this works, we'll upgrade to SSE streaming (Stage 1 full).
