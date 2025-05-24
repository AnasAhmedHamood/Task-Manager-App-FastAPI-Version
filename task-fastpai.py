from fastapi import FastAPI, Form, Request, Depends, status
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
import mysql.connector
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
import os

load_dotenv()

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY") or os.urandom(24))

templates = Jinja2Templates(directory="templates")

# DB connection
db = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)
cursor = db.cursor()

# Logger
def log_action(user_id, action):
    cursor.execute("INSERT INTO logs (user_id, action) VALUES (%s, %s)", (user_id, action))
    db.commit()

# ------------------- ROUTES -------------------

@app.get("/", response_class=HTMLResponse)
def root():
    return RedirectResponse(url="/login")

@app.get("/register", response_class=HTMLResponse)
def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "message": ""})

@app.post("/register")
def register_user(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...)
):
    hashed = generate_password_hash(password)
    try:
        cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (username, email, hashed))
        db.commit()
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    except mysql.connector.errors.IntegrityError:
        return templates.TemplateResponse("register.html", {"request": request, "message": "Username already exists."})

@app.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "message": ""})

@app.post("/login")
def login_user(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    cursor.execute("SELECT * FROM users WHERE name = %s", (username,))
    user = cursor.fetchone()
    if user and check_password_hash(user[3], password):
        request.session["user"] = username
        request.session["user_id"] = user[0]
        log_action(user[0], "Logged in")
        if user[5]:  # is_admin flag
            return RedirectResponse(url="/admin", status_code=status.HTTP_302_FOUND)
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("login.html", {"request": request, "message": "Invalid username or password."})

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    try:
        if "user" not in request.session:
            return RedirectResponse(url="/login")

        uname = request.session["user"]
        cursor.execute("SELECT id FROM users WHERE name = %s", (uname,))
        result = cursor.fetchone()
        if not result:
            return RedirectResponse(url="/login")

        user_id = result[0]
        filter_type = request.query_params.get("filter", "all")

        if filter_type == "completed":
            cursor.execute("SELECT id, task, completed FROM todos WHERE user_id = %s AND completed = 1", (user_id,))
        elif filter_type == "pending":
            cursor.execute("SELECT id, task, completed FROM todos WHERE user_id = %s AND completed = 0", (user_id,))
        else:
            cursor.execute("SELECT id, task, completed FROM todos WHERE user_id = %s", (user_id,))

        tasks = [{"id": row[0], "task": row[1], "completed": row[2]} for row in cursor.fetchall()]
        return templates.TemplateResponse("home.html", {
            "request": request,
            "user": uname,
            "tasks": tasks,
            "filter": filter_type
        })
    except Exception as e:
        return HTMLResponse(f"<h3>DASHBOARD ERROR:</h3><pre>{str(e)}</pre>", status_code=500)

@app.post("/add-task")
def add_task(request: Request, task: str = Form(...)):
    if "user" not in request.session:
        return RedirectResponse(url="/login")

    uname = request.session["user"]
    cursor.execute("SELECT id FROM users WHERE name = %s", (uname,))
    user_id = cursor.fetchone()[0]

    cursor.execute("INSERT INTO todos (user_id, task, completed) VALUES (%s, %s, %s)", (user_id, task, False))
    db.commit()
    log_action(user_id, "Added task")
    return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)

@app.post("/remove-task")
def remove_task(request: Request, task_id: int = Form(...)):
    if "user" not in request.session:
        return RedirectResponse(url="/login")

    user_id = request.session["user_id"]
    cursor.execute("DELETE FROM todos WHERE id = %s", (task_id,))
    db.commit()
    log_action(user_id, f"Removed task ID {task_id}")
    return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)

@app.post("/toggle-task")
def toggle_task(request: Request, task_id: int = Form(...), completed: int = Form(...)):
    if "user" not in request.session:
        return RedirectResponse(url="/login")

    cursor.execute("UPDATE todos SET completed = %s WHERE id = %s", (completed, task_id))
    db.commit()
    action = "Marked task as complete" if completed else "Marked task as incomplete"
    log_action(request.session["user_id"], action)
    return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)

@app.get("/admin", response_class=HTMLResponse)
def admin_dashboard(request: Request):
    if "user" not in request.session:
        return RedirectResponse(url="/login")

    search = request.query_params.get("search", "").strip()
    status_filter = request.query_params.get("status", "")

    base_query = "SELECT id, name, email, is_verified FROM users WHERE is_admin = 0"
    filters = []
    params = []

    if search:
        filters.append("(name LIKE %s OR email LIKE %s)")
        params += [f"%{search}%", f"%{search}%"]

    if status_filter == "verified":
        filters.append("is_verified = 1")
    elif status_filter == "unverified":
        filters.append("is_verified = 0")

    if filters:
        base_query += " AND " + " AND ".join(filters)

    base_query += " ORDER BY id DESC"
    cursor.execute(base_query, params)
    users = cursor.fetchall()

    return templates.TemplateResponse("admin.html", {"request": request, "users": users, "search": search, "status": status_filter})

@app.post("/admin/delete/{user_id}")
def delete_user(user_id: int, request: Request):
    if "user" not in request.session:
        return RedirectResponse(url="/login")

    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
    db.commit()
    return RedirectResponse(url="/admin", status_code=status.HTTP_302_FOUND)

@app.get("/admin/tasks/{user_id}", response_class=HTMLResponse)
def view_user_tasks(user_id: int, request: Request):
    if "user" not in request.session:
        return RedirectResponse(url="/login")

    cursor.execute("SELECT name FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    if not user:
        return HTMLResponse("User not found", status_code=404)

    cursor.execute("SELECT task, completed FROM todos WHERE user_id = %s", (user_id,))
    tasks = cursor.fetchall()

    return templates.TemplateResponse("admin_tasks.html", {"request": request, "user": user[0], "tasks": tasks})

@app.post("/logout")
def logout(request: Request):
    if "user_id" in request.session:
        log_action(request.session["user_id"], "Logged out")
    request.session.clear() if "session" in dir(request) else None
    return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
