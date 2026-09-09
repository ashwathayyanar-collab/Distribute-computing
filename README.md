# Lamport Logical Clock Simulator

Simulates multiple distributed processes exchanging messages and
demonstrates Lamport's logical clock algorithm for event ordering.

## Tech stack
- **Backend:** Python / Flask
- **Frontend:** HTML, CSS, JavaScript
- **Visualization:** D3.js (process timeline with message arrows)
- **Data exchange:** JSON (`POST /api/simulate`)
- **Version control:** Git / GitHub
- **Hosting:** Render (backend) — GitHub Pages cannot host a Flask
  backend, see "Deployment" below
- **Testing:** pytest (unit tests for the clock algorithm)

## Run locally

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000

## Run tests

```bash
pytest tests/ -v
```

## Project structure

```
lamport-sim/
├── app.py                 # Flask routes + API
├── lamport.py              # simulation engine (the actual algorithm)
├── requirements.txt
├── Procfile                 # tells Render/Heroku how to start the app
├── templates/
│   └── index.html
├── static/
│   ├── css/style.css
│   └── js/app.js            # D3.js rendering + fetch() calls to the API
└── tests/
    └── test_lamport.py
```

## Deployment (get a live link)

Flask needs a server to run on, so a purely static host like
**GitHub Pages will not work on its own** — it can only serve HTML/CSS/JS
files, not run Python. Use one of these:

### Option A — Render (recommended, free tier, simplest)
1. Push this folder to a GitHub repository.
2. Go to https://render.com → New → Web Service → connect your repo.
3. Settings:
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `gunicorn app:app`
4. Deploy. Render gives you a live URL like
   `https://lamport-logical-clock-simulator.onrender.com`.

### Option B — Split frontend/backend
- Deploy `app.py` (API only) to Render.
- Host `templates/index.html` + `static/` on GitHub Pages, and change
  the `fetch('/api/simulate')` call in `static/js/app.js` to point at
  your Render URL instead of a relative path.
- Gives you both links mentioned in the report table (GitHub Pages demo
  + GitHub repo), with Render doing the actual computation.

## Resources

| Resource | Link |
|---|---|
| GitHub Repository | https://github.com/\<your-username\>/lamport-logical-clock-simulator |
| Live Demo | https://\<your-app-name\>.onrender.com |
| Clone Command | `git clone https://github.com/<your-username>/lamport-logical-clock-simulator.git` |
