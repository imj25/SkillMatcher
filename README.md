## CV Project

Full‑stack CV processing app with a Django backend and a React frontend.

### Tech stack
- **Backend**: Django
- **Frontend**: React (Create React App)

### Repository layout
- `manage.py`, `cv_app/`, `feedback/`, `templates/`: Django backend
- `frontend/`: React app
- `media/cvs/`: Sample CVs (kept in repo as requested)
- `uploaded_cvs/`: Organized uploaded CVs (kept in repo as requested)
- `scripts/`: Utility scripts (local helpers)

### Quick start

Backend (Django):
1. Create and activate a virtual environment
   - Windows (PowerShell):
     ```bash
     python -m venv .venv
     .venv\\Scripts\\Activate.ps1
     ```
2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```
3. Run migrations and start server
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

Frontend (React):
```bash
cd frontend
npm install
npm start -- --port 3000
```

### Environment variables
1. Copy `.env.example` to `.env` in the project root:
   ```bash
   cp .env.example .env
   ```
2. Edit `.env` and set your values:
   - `SECRET_KEY`: Django secret key (generate a new one for production)
   - `DEBUG`: Set to `False` in production
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `CORS_ALLOWED_ORIGINS`: Comma-separated list of allowed origins (default: `http://localhost:3000`)

For the frontend, create `frontend/.env` if needed:
- `REACT_APP_API_BASE=http://localhost:8000`

### Notes
- Local databases, virtual environments, Node modules, build outputs, and archives are ignored via `.gitignore`.
- Only `media/cvs/` and `uploaded_cvs/` are tracked; other `media` subfolders are ignored.




