# Chat Assistant Experiment

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
