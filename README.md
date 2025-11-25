# AI Workshop - MLCon Berlin 2025

Building Agentic RAG (Retrieval Augmented Generation) systems with LLMs.

## Overview

This workshop walks through building an agentic RAG system step by step:

1. **LLM Clients** - Configure OpenAI and Groq clients
2. **Document Loading** - Load FAQ documents for the knowledge base
3. **Search Index** - Build a searchable index using minsearch
4. **Tool Definition** - Define search tools for LLM function calling
5. **Manual RAG** - Build context-augmented prompts manually
6. **Agentic RAG** - Let the LLM decide when to search (tool calling)
7. **Agentic Loop** - Automate the tool-calling cycle
8. **toyaikit** - Use abstractions for chat interfaces
9. **OpenAI Agents SDK** - Higher-level agent framework
10. **Pydantic AI** - Type-safe agent framework
11. **MCP** - Model Context Protocol for external tools

## Links

- **This repository (fork)**: https://github.com/eyalliebermann/ai-workshop-mlcon-berlin-2025
- **Original repository**: https://github.com/alexeygrigorev/ai-workshop-mlcon-berlin-2025
- **Lecturer's workshop materials**: https://github.com/alexeygrigorev/workshops/tree/main/agents-mcp

## Setup

### 1. Create virtual environment with Python 3.12

```bash
uv venv --python 3.12
```

### 2. Install dependencies

```bash
uv pip install openai python-dotenv requests minsearch ipykernel nbstripout toyaikit pydantic-ai openai-agents
```

### 3. Create Jupyter kernel

```bash
.venv/bin/python -m ipykernel install --user --name ai-workshop-mlcon-berlin-2025 --display-name "ai-workshop-mlcon-berlin-2025"
```

### 4. Configure environment variables

Create a `.env` file with your API keys:

```
OPENAI_API_KEY=your-openai-api-key
GROQ_API_KEY=your-groq-api-key
```

### 5. Activate the virtual environment (optional)

```bash
source .venv/bin/activate
```

### 6. Run the notebook

**Option A: VS Code**

Open `notebook.ipynb` in VS Code and select the **ai-workshop-mlcon-berlin-2025** kernel.

**Option B: Jupyter Notebook**

```bash
uv pip install jupyter notebook
jupyter notebook
```

If running headless:

```bash
jupyter notebook --no-browser
```

Then access it via the URL shown in the terminal (e.g., `http://localhost:8888/tree?token=...`).

## Development

### Git setup for notebook outputs

This repo uses `nbstripout` to automatically strip notebook outputs on commit:

```bash
.venv/bin/nbstripout --install
```

This ensures notebooks are committed without outputs, keeping the repo clean and avoiding merge conflicts.

### Contributing

1. Pull from upstream: `git pull` (fetches from origin)
2. Push your changes: `git push` (pushes to your fork)