📌 Smart Task Analyzer

An intelligent task-prioritization tool built with Django and Vanilla JavaScript, designed to evaluate tasks based on urgency, importance, effort, and dependencies.

This project focuses on:

Algorithm design

Code clarity

Explainability

Clean API design

Smart Task Analyzer

A lightweight Django and JavaScript application that scores and ranks tasks based on urgency, importance, effort, and dependencies.
This project focuses on clean problem-solving, clear API design, and an explainable scoring algorithm.

Tech Stack

Backend: Python, Django, Django REST Framework, SQLite
Frontend: HTML, CSS, JavaScript (Fetch API)

Project Structure

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

How to Run the Project
Backend
cd backend
python -m venv venv
venv\Scripts\activate   # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver


The backend runs at:
http://127.0.0.1:8000/

Frontend

Open frontend/index.html in the browser or run using any simple static server.

API Endpoints
Analyze Tasks

POST /api/tasks/analyze/

Accepts a list of tasks and returns them with calculated scores and explanations.

Suggest Top Tasks

GET /api/tasks/suggest/?limit=3

Returns the top ranked tasks based on the last analysis.

Scoring Approach

Each task is evaluated using four factors:

Urgency (based on due date)

Importance (1–10 scale)

Effort (quick-win factor)

Dependencies (tasks it unblocks)

Four strategies are supported:

Fastest Wins

High Impact

Deadline Driven

Smart Balance (default)

Tasks are scored on a 0–100 scale and categorized into High, Medium, or Low priority. Each task also includes an explanation describing why it received its score.

Testing
cd backend
python manage.py test


Covers importance ranking, past-due handling, dependency cycles, and suggestion limits.

Time Taken

Total implementation time: approximately 3 hours and 45 minutes.

Future Improvements

Dependency graph visualization

Holiday-aware urgency calculations

Eisenhower matrix view

Learning-based scoring adjustments

User accounts and persistent task storage

Notes

This project emphasizes:

A clear and transparent scoring algorithm

Clean and readable code

A simple UI focused on functionality

A well-documented and easy-to-understand backend design