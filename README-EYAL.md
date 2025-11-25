# Setup Instructions

## Create Virtual Environment with Python 3.12

```bash
uv venv --python 3.12
```

## Activate the Virtual Environment

```bash
source .venv/bin/activate
```

## Install Jupyter Notebook

```bash
uv pip install jupyter notebook
```

## Run Jupyter Notebook

```bash
jupyter notebook
```

This will start the Jupyter server and open a browser window. If running headless, use:

```bash
jupyter notebook --no-browser
```

Then access it via the URL shown in the terminal (e.g., `http://localhost:8888/tree?token=...`).
