# ZERVO — Food Redistribution Web Application

ZERVO is an editorial, community-driven food redistribution application designed to bridge the gap between surplus food and neighbors in need.

## Architecture

This project is structured as a monorepo with decoupled frontend and backend:

```text
project-root/
│
├── frontend/
│   ├── assets/
│   ├── components/
│   ├── services/
│   │   └── api.js
│   ├── pages/
│   ├── public/
│   ├── src/
│   ├── index.html
│   ├── login.html
│   ├── signup.html
│   ├── role-selection.html
│   ├── submission.html
│   ├── volunteer-dashboard.html
│   └── ...
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── database/
│   │   ├── core/
│   │   └── utils/
│   ├── requirements.txt
│   ├── .env.example
│   └── .env
│
├── README.md
└── .gitignore
```

---

## Backend Setup (FastAPI + Supabase PostgreSQL)

### 1. Install Dependencies
```bash
cd backend
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Fill in your **Supabase PostgreSQL Connection String**:
```env
SUPABASE_DATABASE_URL=postgresql://postgres.[YOUR-PROJECT-REF]:[YOUR-PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres
```

### 3. Run FastAPI Server
```bash
uvicorn app.main:app --reload --port 8000
```
Interactive API docs available at:
* Swagger UI: `http://localhost:8000/docs`
* ReDoc: `http://localhost:8000/redoc`

---

## Frontend Setup

The frontend consists of organic, high-converting HTML pages with Tailwind CSS styling and an API client (`services/api.js`).

### Run Local Server
```bash
cd frontend
npm start
```
Or open `frontend/index.html` directly in your browser.
