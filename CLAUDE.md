# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Dev
python app.py                          # runs on :5000 with debug=True

# Install deps
pip install -r requirements.txt

# Docker (production)
docker compose up --build -d           # exposes :5003 externally
docker compose logs -f
```

## Environment

Copy `.env.example` → `.env`. Required key: `GEMINI_API_KEY` (used in `/api/generar-propuesta`).

## Architecture

Single-file Flask app (`app.py`). No database. No auth.

**Routes:**
- `GET /` `/about` `/contact` `/propuesta` → render Jinja2 templates
- `POST /api/contact` → logs contact form data (no persistence)
- `POST /api/generar-propuesta` → calls Gemini 1.5 Flash, returns HTML proposal

**Templates** use `templates/base.html` with `templates/components/navbar.html` and `footer.html`. Global template vars (`site_name`, `tagline`, `year`) are injected via `inject_globals()` context processor.

**Static:** `static/css/style.css`, `static/js/main.js`.

**Production:** gunicorn with 4 workers inside Docker, mapped VPS port 5003 → container 5000.
