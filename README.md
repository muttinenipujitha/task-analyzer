# Smart Task Analyzer

A lightweight Django and JavaScript application that prioritizes tasks based on urgency, importance, effort, and dependencies. This project focuses on clean problem-solving, clarity, and an explainable scoring algorithm.

## Tech Stack

**Backend:** Python, Django, Django REST Framework, SQLite  
**Frontend:** HTML, CSS, JavaScript (Fetch API)

## Project Structure

```
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
```

## How to Run

### Backend

```
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Runs at: http://127.0.0.1:8000/

### Frontend

Open `frontend/index.html` in the browser or run via any static server.

## API Endpoints

**POST /api/tasks/analyze/**  
Analyzes and scores the provided tasks.

**GET /api/tasks/suggest/?limit=3**  
Returns top-ranked tasks based on the last analysis.

## Scoring Logic

Each task is evaluated on:

- Urgency  
- Importance  
- Effort (quick-win factor)  
- Dependencies  

Supported strategies:

- Fastest Wins  
- High

- ## Screenshots

### 1. Main Interface
This screenshot shows the initial UI with task input fields, strategy selection, JSON input, and action buttons.

![Main UI](screenshots/main-ui.png)

### 2. Task Analysis Results
This screenshot shows the system in action after analyzing multiple tasks. It displays the calculated scores, priority labels, explanations, and the "Today's Top 3" section.

![Analysis Results](screenshots/results.png)

