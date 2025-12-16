# Todo Task API

A **Django REST Framework (DRF)** backend for managing tasks in a TODO application.
Designed to be simple, scalable, and maintainable.

---

## Features

* User registration and login (JWT-based authentication)
* Create, read, update, and delete tasks
---

## Tech Stack

* **Backend:** Python 3, Django, Django REST Framework
* **Database:** SQLite (for development), Postgresql for production
* **Authentication:** JWT

---

## Installation

```bash
git clone https://github.com/lupppig/todo.git
cd todo
python -m venv venv
source venv/bin/activate 
venv\Scripts\activate   
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

API available at `http://127.0.0.1:8000/`

---

## API Endpoints (examples)

* `POST /api/v1/signup/` — Register a user
* `POST /api/v1/login/` — Login user
* `GET /api/v1/tasks/` — List all tasks
* `POST /api/v1/tasks/` — Create a new task
* `GET /api/v1/tasks/{id}/` — Retrieve a task
* `PUT /api/v1/tasks/{id}/` — Update a task
* `DELETE /api/v1/tasks/{id}/` — Delete a task

Include JWT token in headers for protected endpoints:

```http
Authorization: Bearer <your-token>
```

---

## Running Tests

```bash
python manage.py test
```

Tests cover:

* User authentication
* Task CRUD operations
* Task completion status

---
