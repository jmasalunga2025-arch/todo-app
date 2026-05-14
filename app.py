from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
from functools import wraps
import os

app = Flask(__name__)
app.secret_key = "carabao_secret_key_2024"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE_DIR, "db", "task.db")

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT    UNIQUE NOT NULL,
                password TEXT    NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id  INTEGER NOT NULL,
                task     TEXT    NOT NULL,
                done     INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        conn.commit()

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in first.", "error")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

@app.route("/", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("home"))

    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        with get_db() as conn:
            user = conn.execute(
                "SELECT * FROM users WHERE username = ? AND password = ?",
                (username, password)
            ).fetchone()

        if user:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            flash(f"Welcome back, {user['username']}!", "success")
            return redirect(url_for("home"))
        else:
            flash("Invalid username or password.", "error")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect(url_for("home"))

    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        confirm  = request.form["confirm_password"]

        if not username or not password:
            flash("Username and password are required.", "error")
            return render_template("register.html")

        if password != confirm:
            flash("Passwords do not match.", "error")
            return render_template("register.html")

        try:
            with get_db() as conn:
                conn.execute(
                    "INSERT INTO users (username, password) VALUES (?, ?)",
                    (username, password)
                )
                conn.commit()
            flash("Account created! You can now log in.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Username already taken. Please choose another.", "error")

    return render_template("register.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for("login"))

@app.route("/home")
@login_required
def home():
    filter_type = request.args.get("filter", "all")
    user_id = session["user_id"]

    with get_db() as conn:

        if filter_type == "active":
            tasks = conn.execute(
                "SELECT * FROM tasks WHERE user_id = ? AND done = 0",
                (user_id,)
            ).fetchall()

        elif filter_type == "done":
            tasks = conn.execute(
                "SELECT * FROM tasks WHERE user_id = ? AND done = 1",
                (user_id,)
            ).fetchall()

        else:
            filter_type = "all"
            tasks = conn.execute(
                "SELECT * FROM tasks WHERE user_id = ?",
                (user_id,)
            ).fetchall()

        all_tasks = conn.execute(
            "SELECT done FROM tasks WHERE user_id = ?",
            (user_id,)
        ).fetchall()

    total_tasks = len(all_tasks)
    completed_tasks = sum(1 for t in all_tasks if t["done"] == 1)
    pending_tasks = total_tasks - completed_tasks

    return render_template(
        "home.html",
        user=session["username"],
        tasks=tasks,
        current_filter=filter_type,
        total=total_tasks,
        completed=completed_tasks,
        pending=pending_tasks
    )

@app.route("/about")
@login_required
def about():
    return render_template("about.html")

@app.route("/add", methods=["POST"])
@login_required
def add():
    task_text = request.form.get("task", "").strip()
    if task_text:
        with get_db() as conn:
            conn.execute(
                "INSERT INTO tasks (user_id, task, done) VALUES (?, ?, 0)",
                (session["user_id"], task_text)
            )
            conn.commit()
        flash("Task added!", "success")
    else:
        flash("Task cannot be empty.", "error")
    return redirect(url_for("home"))


@app.route("/done/<int:task_id>")
@login_required
def done(task_id):
    with get_db() as conn:
        task = conn.execute(
            "SELECT * FROM tasks WHERE id = ? AND user_id = ?",
            (task_id, session["user_id"])
        ).fetchone()
        if task:
            new_status = 0 if task["done"] else 1
            conn.execute(
                "UPDATE tasks SET done = ? WHERE id = ? AND user_id = ?",
                (new_status, task_id, session["user_id"])
            )
            conn.commit()
    return redirect(url_for("home"))


@app.route("/edit/<int:task_id>", methods=["GET", "POST"])
@login_required
def edit(task_id):
    with get_db() as conn:
        task = conn.execute(
            "SELECT * FROM tasks WHERE id = ? AND user_id = ?",
            (task_id, session["user_id"])
        ).fetchone()

    if not task:
        flash("Task not found.", "error")
        return redirect(url_for("home"))

    if request.method == "POST":
        new_text = request.form.get("task", "").strip()
        if new_text:
            with get_db() as conn:
                conn.execute(
                    "UPDATE tasks SET task = ? WHERE id = ? AND user_id = ?",
                    (new_text, task_id, session["user_id"])
                )
                conn.commit()
            flash("Task updated!", "success")
            return redirect(url_for("home"))
        else:
            flash("Task cannot be empty.", "error")

    return render_template("edit.html", task=task)


@app.route("/delete/<int:task_id>")
@login_required
def delete(task_id):
    with get_db() as conn:
        conn.execute(
            "DELETE FROM tasks WHERE id = ? AND user_id = ?",
            (task_id, session["user_id"])
        )
        conn.commit()
    flash("Task deleted.", "success")
    return redirect(url_for("home"))

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)