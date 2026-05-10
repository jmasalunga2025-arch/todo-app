from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

# Connect DB
def get_db():
    return sqlite3.connect("db/database.db")

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
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (user, pw))
        result = cursor.fetchone()

        if result:
            session["user_id"] = result[0]
            return redirect("/home")

    return render_template("login.html")

# REGISTER
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user = request.form["username"]
        pw = request.form["password"]

        db = get_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (?,?)", (user, pw))
        db.commit()
        db.close()

        return redirect("/")

    return render_template("register.html")

# HOME
@app.route("/home")
def home():
    if "user_id" not in session:
        return redirect("/")

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM tasks WHERE user_id=?", (session["user_id"],))
    tasks = cursor.fetchall()

    return render_template("index.html", tasks=tasks)

# ADD TASK
@app.route("/add", methods=["POST"])
def add():
    db = get_db()
    cursor = db.cursor()

    cursor.execute("INSERT INTO tasks (user_id, text, done) VALUES (?,?,0)",
                   (session["user_id"], request.form["task"]))
    db.commit()

    return redirect("/home")

# DONE
@app.route("/done/<int:id>")
def done(id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("UPDATE tasks SET done = NOT done WHERE id=?", (id,))
    db.commit()

    return redirect("/home")

# DELETE
@app.route("/delete/<int:id>")
def delete(id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("DELETE FROM tasks WHERE id=?", (id,))
    db.commit()

    return redirect("/home")

app.run(debug=True)