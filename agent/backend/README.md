# Backend

FastAPI + OpenAI GPT-4o-mini

## Setup

```bash
cp .env.example .env
# Add your OPENAI_API_KEY to .env
uv sync
```

## Run

```bash
uv run uvicorn main:app --reload --port 8002
```

## Test

```bash
uv run pytest test_main.py -v
```

## API

```bash
curl -X POST http://127.0.0.1:8002/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What sober events are in Berlin?"}'
```

Docs: http://127.0.0.1:8002/docs

## Structure

```
backend/
├── main.py          # FastAPI app + OpenAI integration
├── test_main.py     # pytest suite
├── pyproject.toml   # uv dependencies
└── .env             # API keys
```
