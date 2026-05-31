from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

from database import get_db_connection, init_db
from business_logic import (
    validate_group_name,
    validate_expense_amount,
    validate_member_count,
    calculate_share,
    calculate_total_expenses,
    calculate_group_summary
)

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

@app.route("/add-group", methods=["GET", "POST"])
def add_group():
    if not is_logged_in():
        return redirect(url_for("login"))

    if request.method == "POST":
        group_name = request.form["group_name"]

        if not validate_group_name(group_name):
            flash("Group name must be at least 2 characters.")
            return redirect(url_for("add_group"))

        conn = get_db_connection()

        conn.execute(
            "INSERT INTO groups (user_id, group_name) VALUES (?, ?)",
            (session["user_id"], group_name.strip())
        )

        conn.commit()
        conn.close()

        flash("Group created successfully.")
        return redirect(url_for("dashboard"))

    return render_template("add_group.html")

@app.route("/group/<int:group_id>")
def group_details(group_id):
    if not is_logged_in():
        return redirect(url_for("login"))

    conn = get_db_connection()

    group = conn.execute(
        "SELECT * FROM groups WHERE id = ? AND user_id = ?",
        (group_id, session["user_id"])
    ).fetchone()

    if group is None:
        conn.close()
        flash("Group not found.")
        return redirect(url_for("dashboard"))

    members = conn.execute(
        "SELECT * FROM members WHERE group_id = ?",
        (group_id,)
    ).fetchall()

    expenses = conn.execute(
        "SELECT * FROM expenses WHERE group_id = ? AND user_id = ? ORDER BY expense_date DESC",
        (group_id, session["user_id"])
    ).fetchall()

    total_expenses = calculate_total_expenses(expenses)
    expense_summary = calculate_group_summary(expenses)

    conn.close()

    return render_template(
        "group_details.html",
        group=group,
        members=members,
        expenses=expenses,
        total_expenses=total_expenses,
        expense_summary=expense_summary
    )


@app.route("/group/<int:group_id>/add-member", methods=["POST"])
def add_member(group_id):
    if not is_logged_in():
        return redirect(url_for("login"))

    member_name = request.form["member_name"]

    conn = get_db_connection()

    group = conn.execute(
        "SELECT * FROM groups WHERE id = ? AND user_id = ?",
        (group_id, session["user_id"])
    ).fetchone()

    if group is None:
        conn.close()
        flash("Group not found.")
        return redirect(url_for("dashboard"))

    if len(member_name.strip()) < 2:
        conn.close()
        flash("Member name must be at least 2 characters.")
        return redirect(url_for("group_details", group_id=group_id))

    conn.execute(
        "INSERT INTO members (group_id, member_name) VALUES (?, ?)",
        (group_id, member_name.strip())
    )

    conn.commit()
    conn.close()

    flash("Member added successfully.")
    return redirect(url_for("group_details", group_id=group_id))

@app.route("/group/<int:group_id>/add-expense", methods=["GET", "POST"])
def add_expense(group_id):
    if not is_logged_in():
        return redirect(url_for("login"))

    conn = get_db_connection()

    group = conn.execute(
        "SELECT * FROM groups WHERE id = ? AND user_id = ?",
        (group_id, session["user_id"])
    ).fetchone()

    if group is None:
        conn.close()
        flash("Group not found.")
        return redirect(url_for("dashboard"))

    members = conn.execute(
        "SELECT * FROM members WHERE group_id = ?",
        (group_id,)
    ).fetchall()

    if request.method == "POST":
        title = request.form["title"].strip()
        amount = float(request.form["amount"])
        paid_by = request.form["paid_by"]
        expense_date = request.form["expense_date"]
        notes = request.form["notes"]

        split_count = len(members)

        if not validate_member_count(split_count):
            flash("You need at least 2 members to split expenses.")
            conn.close()
            return redirect(url_for("group_details", group_id=group_id))

        if len(title) < 3:
            flash("Expense title must be at least 3 characters.")
            conn.close()
            return redirect(url_for("add_expense", group_id=group_id))

        if not validate_expense_amount(amount):
            flash("Amount must be greater than zero.")
            conn.close()
            return redirect(url_for("add_expense", group_id=group_id))

        conn.execute(
            """
            INSERT INTO expenses 
            (user_id, group_id, title, amount, paid_by, split_count, expense_date, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                session["user_id"],
                group_id,
                title,
                amount,
                paid_by,
                split_count,
                expense_date,
                notes
            )
        )

        conn.commit()
        conn.close()

        flash("Expense added successfully.")
        return redirect(url_for("group_details", group_id=group_id))

    conn.close()

    return render_template("add_expense.html", group=group, members=members)

@app.route("/expense/<int:expense_id>/delete", methods=["POST"])
def delete_expense(expense_id):
    if not is_logged_in():
        return redirect(url_for("login"))

    conn = get_db_connection()

    expense = conn.execute(
        "SELECT * FROM expenses WHERE id = ? AND user_id = ?",
        (expense_id, session["user_id"])
    ).fetchone()

    if expense is None:
        conn.close()
        flash("Expense not found.")
        return redirect(url_for("dashboard"))

    group_id = expense["group_id"]

    conn.execute(
        "DELETE FROM expenses WHERE id = ? AND user_id = ?",
        (expense_id, session["user_id"])
    )

    conn.commit()
    conn.close()

    flash("Expense deleted successfully.")
    return redirect(url_for("group_details", group_id=group_id))

@app.route("/expense/<int:expense_id>/edit", methods=["GET", "POST"])
def edit_expense(expense_id):
    if not is_logged_in():
        return redirect(url_for("login"))

    conn = get_db_connection()

    expense = conn.execute(
        "SELECT * FROM expenses WHERE id = ? AND user_id = ?",
        (expense_id, session["user_id"])
    ).fetchone()

    if expense is None:
        conn.close()
        flash("Expense not found.")
        return redirect(url_for("dashboard"))

    group_id = expense["group_id"]

    group = conn.execute(
        "SELECT * FROM groups WHERE id = ? AND user_id = ?",
        (group_id, session["user_id"])
    ).fetchone()

    members = conn.execute(
        "SELECT * FROM members WHERE group_id = ?",
        (group_id,)
    ).fetchall()

    if request.method == "POST":
        title = request.form["title"].strip()
        amount = float(request.form["amount"])
        paid_by = request.form["paid_by"]
        expense_date = request.form["expense_date"]
        notes = request.form["notes"]

        split_count = len(members)

        if len(title) < 3:
            flash("Expense title must be at least 3 characters.")
            conn.close()
            return redirect(url_for("edit_expense", expense_id=expense_id))

        if not validate_expense_amount(amount):
            flash("Amount must be greater than zero.")
            conn.close()
            return redirect(url_for("edit_expense", expense_id=expense_id))

        conn.execute(
            """
            UPDATE expenses
            SET title = ?, amount = ?, paid_by = ?, split_count = ?, expense_date = ?, notes = ?
            WHERE id = ? AND user_id = ?
            """,
            (
                title,
                amount,
                paid_by,
                split_count,
                expense_date,
                notes,
                expense_id,
                session["user_id"]
            )
        )

        conn.commit()
        conn.close()

        flash("Expense updated successfully.")
        return redirect(url_for("group_details", group_id=group_id))

    conn.close()

    return render_template(
        "edit_expense.html",
        expense=expense,
        group=group,
        members=members
    )

if __name__ == "__main__":
    app.run(debug=True)