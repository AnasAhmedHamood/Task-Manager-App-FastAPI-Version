# task-manager-app-FastAPI-Version

A simple task manager built with FastAPI using MySQL and Jinja2 templates.

---

## ✨ Features

* User registration and login
* Secure password hashing
* Session-based authentication
* Add, delete, and toggle task status
* Filter tasks (all, completed, pending)
* Admin dashboard for user management
* Admin can view tasks of any user
* Logs user actions like login/logout/task edits

---

## 🛠 Tech Stack

* **Backend:** FastAPI
* **Frontend:** HTML + Jinja2 templates
* **Database:** MySQL
* **Authentication:** SessionMiddleware
* **Password Security:** Werkzeug
* **Environment Config:** python-dotenv

---

## 🖼 Screenshots

* ![Register](https://github.com/user-attachments/assets/70cf6dbf-1c8b-4531-bfc0-ba14701849d6)
* ![Login](https://github.com/user-attachments/assets/2425e232-bf77-438c-9020-b6cec84c98ad)
* ![Dashboard with Filter](https://github.com/user-attachments/assets/94cf35bb-4f04-4385-9a5a-fec8d33fab5e)
* ![Dashboard Typing](https://github.com/user-attachments/assets/eec42637-5759-482e-b199-6e6ccded8014)
* ![Dashboard Task Added](https://github.com/user-attachments/assets/32674452-3e56-458d-8370-3b71c5d431d1)
* ![Admin Login](https://github.com/user-attachments/assets/e4991292-ef00-4640-9655-9327c2c0db01)
* ![Admin Dashboard](https://github.com/user-attachments/assets/301f4475-ddce-43ef-a1ca-d28422efff5b)
* ![User Tasks](https://github.com/user-attachments/assets/308e6dfa-cbe6-446d-8bd1-9b62a1281fda)


---

## ✏️ How to Run (VS Code)

Before you run this project, make sure you have the following installed:

* [Python 3.8+](https://www.python.org/downloads/)
* [MySQL Server](https://dev.mysql.com/downloads/mysql/)
* [Visual Studio Code](https://code.visualstudio.com/)

### From VS Code Terminal:

1. Install required Python packages:

```bash
pip install fastapi uvicorn jinja2 mysql-connector-python python-dotenv werkzeug
```

2. Run the app:

```bash
uvicorn task-fastapi:app --reload
```

Or:

```bash
python -m uvicorn task-fastapi:app --reload
```

3. Open your browser:
   Hold `Ctrl` and click on: [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## 📂 Project Structure

```pgsql
.
├── task-fastapi.py
├── templates/
│   ├── login.html
│   ├── register.html
│   ├── home.html
│   ├── admin.html
│   └── admin_tasks.html
├── Check-DB.py
├── .gitignore
└── README.md
```

---

## 👨‍💻 Author

**Anas Ahmed Hamood**

---

## 📄 License

This project is licensed under the MIT License.
