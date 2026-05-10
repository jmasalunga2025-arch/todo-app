from flask import Flask, render_template, request, redirect, session, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "secret123"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "db", "database.db")

# Connect DB
def get_db():
    return sqlite3.connect(DB_PATH)

# Create tables
def init_db():
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        text TEXT,
        done INTEGER
    )
    """)

    db.commit()
    db.close()

init_db()

# LOGIN
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form["username"]
        pw = request.form["password"]

        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (user, pw)
        )
        result = cursor.fetchone()
        db.close()

        if result:
            session["user_id"] = result[0]
            return redirect("/home")
        else:
            flash("Invalid username or password!", "error")

    return render_template("login.html")

# REGISTER
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user = request.form["username"]
        pw = request.form["password"]

        db = get_db()
        cursor = db.cursor()

        cursor.execute("SELECT * FROM users WHERE username=?", (user,))
        existing = cursor.fetchone()

        if existing:
            flash("Username already exists!", "error")
            return redirect("/register")

        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?,?)",
            (user, pw)
        )

        db.commit()
        db.close()

        flash("Account created successfully!", "success")
        return redirect("/")

    return render_template("register.html")

# HOME
@app.route("/home")
def home():
    if "user_id" not in session:
        return redirect("/")

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "SELECT * FROM tasks WHERE user_id=?",
        (session["user_id"],)
    )
    tasks = cursor.fetchall()
    db.close()

    return render_template("index.html", tasks=tasks)

# ADD TASK
@app.route("/add", methods=["POST"])
def add():
    if "user_id" not in session:
        return redirect("/")

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "INSERT INTO tasks (user_id, text, done) VALUES (?,?,0)",
        (session["user_id"], request.form["task"])
    )

    db.commit()
    db.close()

    return redirect("/home")

# TOGGLE DONE
@app.route("/done/<int:id>")
def done(id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "UPDATE tasks SET done = CASE WHEN done=1 THEN 0 ELSE 1 END WHERE id=?",
        (id,)
    )

    db.commit()
    db.close()

    return redirect("/home")

# DELETE TASK
@app.route("/delete/<int:id>")
def delete(id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("DELETE FROM tasks WHERE id=?", (id,))

    db.commit()
    db.close()

    return redirect("/home")

# EDIT TASK
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    db = get_db()
    cursor = db.cursor()

    if request.method == "POST":
        new_text = request.form["task"]

        cursor.execute(
            "UPDATE tasks SET text=? WHERE id=?",
            (new_text, id)
        )
        db.commit()
        db.close()

        return redirect("/home")

    cursor.execute("SELECT * FROM tasks WHERE id=?", (id,))
    task = cursor.fetchone()
    db.close()

    return render_template("edit.html", task=task)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)