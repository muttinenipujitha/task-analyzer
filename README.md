📌 Smart Task Analyzer

An intelligent task-prioritization tool built with Django and Vanilla JavaScript, designed to evaluate tasks based on urgency, importance, effort, and dependencies.

This project focuses on:

Algorithm design

Code clarity

Explainability

Clean API design

🚀 Tech Stack
Backend

Python 3.8+

Django 4.x

Django REST Framework

django-cors-headers

SQLite

Frontend

HTML5, CSS3, JavaScript

Fetch API for HTTP calls

📁 Project Structure
task-analyzer/
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── task_analyzer/
│   └── tasks/
└── frontend/
    ├── index.html
    ├── styles.css
    └── script.js

🛠️ Setup Instructions
1. Run the Backend
cd backend
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate  # Mac/Linux

pip install -r requirements.txt
python manage.py migrate
python manage.py runserver


Backend runs at:
➡️ http://127.0.0.1:8000/

2. Run the Frontend

Open:

frontend/index.html


(or use VS Code Live Server)

The frontend communicates with:

http://127.0.0.1:8000/api/tasks/...

📌 API Endpoints
1. Analyze Tasks
POST /api/tasks/analyze/


Request format:

{
  "strategy": "smart_balance",
  "tasks": [
    {
      "id": "T1",
      "title": "Fix login bug",
      "due_date": "2025-11-30",
      "estimated_hours": 3,
      "importance": 8,
      "dependencies": []
    }
  ]
}

2. Suggest Top Tasks
GET /api/tasks/suggest/?strategy=smart_balance&limit=3


Returns top tasks ranked by priority.

🧠 Priority Algorithm – Simple Explanation

Each task receives a score (0–100) based on:

✔ Urgency

How soon the task is due (past-due = highest urgency)

✔ Importance

User rating (1–10 → normalized)

✔ Effort (Quick-Win Factor)

Small tasks are promoted as “quick wins”

✔ Dependency Breadth

Tasks that unblock others get boosted

Each strategy uses different weight combinations:

Fastest Wins

High Impact

Deadline Driven

Smart Balance (default)

Explanations describe why a task ranked high.

🧪 Tests

Run:

cd backend
python manage.py test


Includes:

Importance comparison

Past-due urgency

Circular dependency detection

Suggest-endpoint limit tests

⏳ Time Breakdown
Work Item	Time
Algorithm design	1h 15m
Backend implementation	45m
Frontend UI + JS	1h
Tests + README + cleanup	45m

Total ≈ 3h 45m

🌱 Future Enhancements

Visual dependency graph

Holiday-aware urgency

Eisenhower matrix UI

ML-based weight adjustments

User accounts & persistent tasks

📝 Notes for Reviewers

Code is intentionally clean and readable

Algorithm is explainable and configurable

UI demonstrates core features without unnecessary complexity