# AARN backend (FastAPI)

## Local quickstart

1. Create virtualenv and install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Run server

```bash
uvicorn app.main:app --reload --port 8000
```

3. Visit http://localhost:8000/docs for OpenAPI UI

## Environment

- DATABASE_URL (default sqlite:///./database.db)
- OPENAI_API_KEY (optional)
- S2_API_BASE (optional)

```


---


# Next steps


- I can export this skeleton as a downloadable ZIP.
- I can also generate the `admin-ui/` Streamlit app files that call this backend.
- I can flesh out any file further (e.g. implement robust LLM prompt templates, add PDF parsing helpers, add Alembic migrations, or add unit tests).
```

# setting environmet

setx S2_API_KEY "你的真正 API KEY"
echo $env:S2_API_KEY

or simply
$env:S2_API_KEY="your api key"
