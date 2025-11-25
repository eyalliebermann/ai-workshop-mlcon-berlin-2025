# ai-workshop-mlcon-berlin-2025

## Setup

### 1. Create virtual environment with Python 3.12

```bash
uv venv --python 3.12
```

### 2. Install dependencies

```bash
uv pip install openai python-dotenv requests minsearch ipykernel
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