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

### Implementaiton

FastAPI + OpenAI GPT-4o-mini

#### Setup

```bash
cp .env.example .env
# Add your OPENAI_API_KEY to .env
uv sync
```

#### Run

```bash
uv run uvicorn main:app --reload --port 8002
```

#### Test

```bash
uv run pytest test_main.py -v
```

#### API

```bash
curl -X POST http://127.0.0.1:8002/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What sober events are in Berlin?"}'
```

Docs: http://127.0.0.1:8002/docs

#### Structure

```
backend/
├── main.py          # FastAPI app + OpenAI integration
├── test_main.py     # pytest suite
├── pyproject.toml   # uv dependencies
└── .env             # API keys
```


---
---

# TODO MERGE THIS IN OR REMOVE 

Build a simple chat assistant with a backend API and frontend interface.

## Goal

Create a working chat interface where:
1. User types a message in a web frontend
2. Frontend sends message to backend API
3. Backend processes and returns a response
4. Frontend displays the response

## Plan

### Phase 1: Backend (No LLM - Text Reversal Logic)

Create a minimal backend that receives text and returns it reversed.

**Tech choice:** Python + FastAPI
- Simple, fast to set up
- Built-in OpenAPI docs
- Easy async support

**Steps:**
1. Create `main.py` with FastAPI app
2. Add POST `/chat` endpoint accepting `{"message": "..."}`
3. Return `{"response": "..."}` with reversed text
4. Add CORS middleware for frontend access

### Phase 2: Frontend (Simple Chat UI)

Create a minimal web interface to interact with the backend.

**Tech choice:** Plain HTML + JavaScript
- No build step required
- Serves from a simple static file
- Easy to understand and modify

**Steps:**
1. Create `index.html` with chat interface
2. Add message input and send button
3. Display conversation history
4. Connect to backend via fetch API

### Phase 3: Integration & Testing

Wire everything together and verify it works.

**Steps:**
1. Run backend server
2. Open frontend in browser
3. Send test messages and verify reversed responses appear

---

## Implementation Checklist

- [x] Phase 1: Backend
  - [x] Create FastAPI app with `/chat` endpoint
  - [x] Add text reversal logic
  - [x] Add CORS middleware
  - [x] Test with curl

- [ ] Phase 2: Frontend
  - [ ] Create HTML chat interface
  - [ ] Add JavaScript for API calls
  - [ ] Style for basic usability

- [ ] Phase 3: Integration
  - [ ] Run both services
  - [ ] Verify end-to-end chat works

---

## Running the Application

### Backend
```bash
cd backend
uv run uvicorn main:app --reload --port 8001
```

### Frontend
```bash
# Simply open frontend/index.html in a browser
# Or serve it:
cd frontend
python -m http.server 3000
```

Then open http://localhost:3000 in your browser.
