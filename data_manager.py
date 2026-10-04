import json
import os
import uuid
from datetime import datetime

DATA_FILE = os.path.join(os.path.dirname(__file__), 'data', 'projects.json')

def _ensure_data_file():
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    if not os.path.exists(DATA_FILE):
        _seed_data()

def _seed_data():
    seed = [
        {
            "id": str(uuid.uuid4()),
            "idea": "Build a college attendance management system",
            "options": {"type": "Web App", "stack": "Python/Flask", "team": "1-3"},
            "created": datetime.now().isoformat(),
            "status": "Finished",
            "documents": {
                "prd": "# PRD: College Attendance System\n\n## Overview\nA system to track student attendance digitally.\n## Features\n- Teacher portal\n- Student view\n- Admin dashboard",
                "trd": "# TRD\n\n## Tech Stack\n- Flask\n- SQLite\n- Bootstrap",
                "architecture": "# Architecture\nMonolithic web application with role-based access control.",
                "database": "# Database Schema\n\n| Table | Columns |\n|---|---|\n| Users | id, name, role |\n| Attendance | id, user_id, date, status |",
                "api": "# APIs\n\n`POST /api/attendance`\n- Purpose: Mark attendance",
                "ui": "# UI Brief\nMinimalist interface. Clear tables for records.",
                "steps": "- [x] Setup repo\n- [x] Create Auth\n- [ ] Build Dashboard",
                "diagram": "graph TD\n    A[Teacher] --> B[Login]\n    B --> C[Select Class]\n    C --> D[Mark Attendance]"
            },
            "history": [{"timestamp": datetime.now().isoformat(), "action": "Created", "details": "Seed project loaded"}]
        },
        {
            "id": str(uuid.uuid4()),
            "idea": "E-commerce platform for custom mechanical keyboards",
            "options": {"type": "Web App", "stack": "Node.js/React", "team": "4-10"},
            "created": datetime.now().isoformat(),
            "status": "Finished",
            "documents": {
                "prd": "# PRD: Keycap E-commerce\n\n## Overview\nPlatform for selling custom keycaps and keyboards.",
                "trd": "# TRD\n\n## Tech Stack\n- React\n- Express\n- Stripe API",
                "architecture": "# Architecture\nHeadless commerce architecture with SPA frontend.",
                "database": "# Database Schema\n\n| Table | Columns |\n|---|---|\n| Products | id, name, price, stock |\n| Orders | id, user_id, total, status |",
                "api": "# APIs\n\n`GET /api/products`\n- Purpose: List items",
                "ui": "# UI Brief\nDark theme, high-res images, interactive keyboard visualizer.",
                "steps": "- [x] Initial design\n- [ ] Integrate Stripe",
                "diagram": "graph TD\n    A[Customer] --> B[Browse Products]\n    B --> C[Add to Cart]\n    C --> D[Checkout & Pay]"
            },
            "history": [{"timestamp": datetime.now().isoformat(), "action": "Created", "details": "Seed project loaded"}]
        }
    ]
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(seed, f, indent=4)

def load_projects():
    _ensure_data_file()
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_projects(projects):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(projects, f, indent=4)

def get_project(project_id):
    projects = load_projects()
    for p in projects:
        if p['id'] == project_id:
            return p
    return None

def update_project(project_id, updates):
    projects = load_projects()
    for i, p in enumerate(projects):
        if p['id'] == project_id:
            projects[i].update(updates)
            save_projects(projects)
            return projects[i]
    return None

def create_project(idea, options):
    projects = load_projects()
    new_project = {
        "id": str(uuid.uuid4()),
        "idea": idea,
        "options": options,
        "created": datetime.now().isoformat(),
        "status": "Draft",
        "documents": {},
        "history": [{"timestamp": datetime.now().isoformat(), "action": "Initialized", "details": "Project created"}]
    }
    projects.insert(0, new_project)
    save_projects(projects)
    return new_project

def delete_project(project_id):
    projects = load_projects()
    projects = [p for p in projects if p['id'] != project_id]
    save_projects(projects)