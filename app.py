from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

from database import get_db_connection, init_db

app = Flask(__name__)
app.secret_key = "splitmate_secret_key"


def is_logged_in():
    return "user_id" in session


@app.route("/")
def index():
    if is_logged_in():
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/init-db")
def initialize_database():
    init_db()
    return "Database initialized successfully!"


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        if len(username) < 3:
            flash("Username must be at least 3 characters.")
            return redirect(url_for("register"))

        if len(password) < 4:
            flash("Password must be at least 4 characters.")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password)

        conn = get_db_connection()

        try:
            conn.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, hashed_password)
            )
            conn.commit()
        except:
            flash("Username already exists.")
            conn.close()
            return redirect(url_for("register"))

        conn.close()
        flash("Account created successfully. Please login.")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        conn = get_db_connection()

        user = conn.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchone()

        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("dashboard"))

        flash("Invalid username or password.")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for("login"))


@app.route("/dashboard")
def dashboard():
    if not is_logged_in():
        return redirect(url_for("login"))

    conn = get_db_connection()

    groups = conn.execute(
        """
        SELECT groups.*,
               COUNT(DISTINCT members.id) AS member_count,
               COUNT(DISTINCT expenses.id) AS expense_count
        FROM groups
        LEFT JOIN members ON groups.id = members.group_id
        LEFT JOIN expenses ON groups.id = expenses.group_id
        WHERE groups.user_id = ?
        GROUP BY groups.id
        ORDER BY groups.created_at DESC
        """,
        (session["user_id"],)
    ).fetchall()

    conn.close()

    return render_template("dashboard.html", groups=groups)


if __name__ == "__main__":
    app.run(debug=True)