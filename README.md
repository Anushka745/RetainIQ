# RetainIQ

**AI-powered user analytics and churn prediction platform.**

RetainIQ explains *why* users are leaving, *where* they're dropping off, and *what* to do about it — combining a FastAPI backend, a scikit-learn churn model, and a Streamlit dashboard frontend.

---

## Architecture

This is a **two-server application**:

```
┌─────────────────┐         HTTP/JSON          ┌──────────────────┐
│  Streamlit       │  ──────────────────────►   │  FastAPI Backend │
│  Frontend        │  ◄──────────────────────   │  (port 8000)     │
│  (port 8501)     │      JWT Bearer auth        │                  │
└─────────────────┘                              └──────────────────┘
                                                          │
                                                          ▼
                                                   SQLite (retainiq.db)
```

The frontend never talks to the database directly — every page calls the FastAPI backend over HTTP using `requests`, the same way a real production frontend would.

---

## Folder Structure

```
RetainIQ/
├── backend/
│   ├── main.py                 # FastAPI app entrypoint
│   ├── database.py             # SQLAlchemy engine/session
│   ├── models.py                # ORM models: User, EndUser, UserSession, Event, Prediction
│   ├── schemas.py               # Pydantic request/response schemas
│   ├── auth_utils.py             # JWT + bcrypt helpers
│   ├── rate_limiter.py           # In-memory rate limiting
│   ├── seed.py                   # Seeds admin account + 250 sample end-users
│   ├── requirements.txt
│   ├── routers/
│   │   ├── auth.py               # /auth/* endpoints
│   │   ├── dashboard.py          # /dashboard
│   │   ├── users.py              # /users, /upload
│   │   ├── churn.py              # /churn
│   │   ├── funnel.py             # /funnel
│   │   ├── cohorts.py            # /cohorts
│   │   └── insights.py           # /insights
│   └── services/
│       ├── churn_model.py        # scikit-learn RandomForest churn predictor
│       ├── segmentation.py       # Rule-based user segmentation
│       ├── funnel_engine.py      # Funnel conversion/drop-off math
│       ├── cohort_engine.py      # Monthly cohort retention
│       └── insights_engine.py    # Rule-based AI insights (+ optional Ollama)
├── frontend/
│   ├── app.py                    # Landing / home page
│   ├── requirements.txt
│   ├── pages/
│   │   ├── login.py
│   │   ├── signup.py
│   │   ├── dashboard.py
│   │   ├── user_analytics.py
│   │   ├── funnel_analysis.py
│   │   ├── churn_prediction.py
│   │   ├── cohort_analysis.py
│   │   ├── ai_insights.py
│   │   └── settings.py
│   ├── components/
│   │   ├── navbar.py
│   │   ├── metric_cards.py
│   │   └── charts.py
│   ├── utils/
│   │   ├── api_client.py
│   │   └── helpers.py
│   └── assets/
│       └── theme.py              # Custom CSS (dark/light mode)
├── data/
│   └── sample_users.csv          # 150-row sample dataset for CSV upload testing
└── README.md
```

---

## Setup & Run (Local Development)

You'll need **two terminal windows** — one for the backend, one for the frontend.

### 1. Backend (FastAPI)

```bash
cd RetainIQ/backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Seed the database with the admin account + 250 sample users
python seed.py

# Start the API server
uvicorn main:app --reload --port 8000
```

The API is now live at `http://localhost:8000`. Interactive docs: `http://localhost:8000/docs`.

### 2. Frontend (Streamlit)

In a **second terminal**:

```bash
cd RetainIQ/frontend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

streamlit run app.py
```

The app opens at `http://localhost:8501`.

### 3. Log in

Use the seeded demo admin account:

```
Email:    admin@retainiq.com
Password: Admin@123
```

> ⚠️ **Security note:** This demo account's password is intentionally simple and is hashed with bcrypt before being stored — but it is **publicly known** (it's printed right here in this README). Change its password or delete the account before deploying anywhere publicly accessible.

You can also click **Create one here** on the login page to sign up your own account.

---

## Uploading Your Own Data

Go to **Settings → Import Data** and upload a CSV with these columns:

| Column | Required | Type | Notes |
|---|---|---|---|
| `external_id` | Yes | string | Unique user identifier |
| `signup_date` | Yes | date | `YYYY-MM-DD` |
| `name` | No | string | |
| `email` | No | string | |
| `last_active_date` | No | date | `YYYY-MM-DD` |
| `plan` | No | string | e.g. `free`, `starter`, `pro`, `enterprise` |
| `revenue` | No | float | |
| `sessions_count` | No | int | |
| `features_used` | No | int | |
| `is_churned` | No | bool | `True`/`False` |

A ready-to-use sample file is included at `data/sample_users.csv`.

---

## Environment Variables (optional)

Set these before starting the backend to override defaults:

| Variable | Default | Purpose |
|---|---|---|
| `DATABASE_URL` | `sqlite:///retainiq.db` | SQLAlchemy connection string |
| `JWT_SECRET_KEY` | dev placeholder | **Set a strong random value in production** |
| `OLLAMA_ENABLED` | `false` | Set `true` to enrich AI Insights using a local Ollama model |
| `OLLAMA_URL` | `http://localhost:11434/api/generate` | Ollama server endpoint |
| `OLLAMA_MODEL` | `llama3` | Ollama model name |

For the frontend:

| Variable | Default | Purpose |
|---|---|---|
| `RETAINIQ_BACKEND_URL` | `http://localhost:8000` | URL the Streamlit app calls for the API |

---

## Deployment

### Option A: Render / Railway (backend) + Streamlit Cloud (frontend)

**Backend on Render/Railway:**
1. Push the `backend/` folder to a Git repo (or the whole `RetainIQ/` repo).
2. Create a new Web Service pointing at `backend/`.
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Set `JWT_SECRET_KEY` to a strong random secret in the service's environment variables.
6. Run `python seed.py` once via the platform's shell/console (or a one-off job) to seed the database.

**Frontend on Streamlit Cloud:**
1. Push the `frontend/` folder to a Git repo.
2. Create a new app on [share.streamlit.io](https://share.streamlit.io), pointing at `frontend/app.py`.
3. In the app's "Secrets", set:
   ```toml
   RETAINIQ_BACKEND_URL = "https://your-backend-url.onrender.com"
   ```
4. Deploy.

> Note: SQLite on Render/Railway free tiers may not persist across redeploys/restarts unless you attach a persistent disk. For production use, consider switching `DATABASE_URL` to a managed Postgres instance — SQLAlchemy makes this a one-line config change.

### Option B: Single VM / Docker Compose (both services together)

Run both processes on one machine (e.g. a VM, or two containers in Compose):

```bash
# Backend
uvicorn main:app --host 0.0.0.0 --port 8000 &

# Frontend (point it at the backend on localhost)
RETAINIQ_BACKEND_URL=http://localhost:8000 streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

Expose port `8501` to the public internet (and keep `8000` internal-only if you don't need direct API access).

---

## Security Notes

- Passwords are hashed with **bcrypt** (via `passlib`) — never stored in plaintext.
- Authentication uses **JWT bearer tokens**, validated on every protected endpoint via a FastAPI dependency.
- A lightweight **in-memory rate limiter** protects `/auth/login` and `/auth/signup` (10 req/min/IP) and general endpoints (120 req/min/IP). For multi-instance production deployments, replace this with a Redis-backed limiter, since in-memory state doesn't share across processes.
- CORS is currently open (`allow_origins=["*"]`) for ease of local development — **restrict this to your actual frontend origin before deploying publicly.**
- SQL injection is mitigated by using SQLAlchemy's ORM/query builder throughout (no raw string-interpolated SQL).
- Input validation is enforced via Pydantic schemas on every request body.

---

## Tech Stack

- **Frontend:** Streamlit, Plotly, Pandas
- **Backend:** FastAPI, SQLAlchemy, SQLite, Pydantic
- **Auth:** python-jose (JWT), passlib + bcrypt
- **ML:** scikit-learn (RandomForestClassifier for churn prediction)
- **AI Insights:** Rule-based engine, with optional local Ollama LLM augmentation

---

## Known Limitations

- Streamlit doesn't support real browser-level routing/redirects — page access control is implemented via `st.session_state` checks at the top of each page (`require_login()`), not URL-level guards. The backend, not the frontend, is the actual security boundary: every protected API call separately validates the JWT.
- The churn model retrains on every `/churn` and `/insights` request rather than being persisted/cached. This keeps the demo simple but would be a good first optimization for a high-traffic deployment (e.g. retrain on a schedule and cache the model).
- The in-memory rate limiter resets if the backend process restarts and doesn't share state across multiple backend instances.
