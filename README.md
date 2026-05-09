# Smart Task Management System

## summary

This project is a task management web app built with Python and Flask. The goal was to create a clean, simple system that shows my understanding of backend development, database design, and basic frontend integration.

## About the project does

- Lets a user register and log in
- Allows creating, updating, deleting, and viewing tasks
- Supports task priority and status tracking
- Shows task analytics like total, pending, and completed tasks
- Uses WebSockets for live updates
- Provides a simple responsive browser interface

## features  built it this way

- I used Flask because it is lightweight and easy to explain in an interview
- I separated the code into folders like models, routes, services, and config so the project stays organized
- I used PostgreSQL in the main version to show real database work

## Main folders

- `app/` - backend code, API routes, and business logic
- `config/` - settings, database connection, and schema
- `templates/` - HTML pages
- `static/` - CSS and JavaScript files

## How to run

1. Open PowerShell in this folder.
2. Activate the virtual environment:

```powershell
.\venv\Scripts\activate
```

3. Start the main app:

```powershell
python app.py
```


## Open in browser

After the app starts, open:

http://localhost:5000
