# SplitMate — Shared Expense Manager

SplitMate is a Flask web application designed to help users manage shared expenses inside groups.
Users can create expense groups, add members, record shared expenses, and automatically calculate each person's share.

This project was developed as a Software Engineering final project using Flask, SQLite, raw SQL, sessions, and unit testing.

---

## Project Idea

The main idea of SplitMate is to make shared payments easier to manage.

Example use cases:

* Roommates sharing house expenses
* Friends splitting trip costs
* Students sharing group activity payments
* Team members tracking shared purchases

Each user has their own account and can only access their own groups, members, and expenses.

---

## Features

* User registration
* User login and logout
* Session-based authentication
* Multi-user data separation
* Create expense groups
* Add members to groups
* Add shared expenses
* Automatically calculate each member's share
* View total group expenses
* Edit expenses
* Delete expenses
* Basic unit tests for business logic

---

## Technologies Used

* Python
* Flask
* SQLite
* Raw SQL
* HTML
* CSS
* Pytest
* Git and GitHub

---

## Database Structure

The application uses SQLite with raw SQL only.

Main tables:

### users

Stores registered users.

### groups

Stores expense groups created by users.
Each group is linked to a user using `user_id`.

### members

Stores members inside each group.

### expenses

Stores shared expenses.
Each expense is linked to a user and a group.

---

## Business Logic

The project includes separate business logic functions, such as:

* Calculating each person's share
* Validating expense amounts
* Validating group names
* Validating member names
* Checking if a group has enough members
* Calculating total group expenses
* Creating expense summaries

These functions are tested using Pytest.

---

## User Stories

### US1 — Create Expense Group

As a user, I want to create an expense group so that I can manage shared payments with specific people.

Acceptance Criteria:

* The user can create a group with a valid group name.
* The group is saved under the logged-in user's account.
* The user can see only their own groups.
* Empty or very short group names are rejected.

---

### US2 — Manage Group Members

As a user, I want to add members to a group so that expenses can be split between them.

Acceptance Criteria:

* The user can add members to one of their own groups.
* Member names must be valid.
* The members appear on the group details page.
* A group must have at least two members before adding an expense.

---

### US3 — Add Shared Expense

As a user, I want to add a shared expense so that the system calculates each person's share.

Acceptance Criteria:

* The user can add title, amount, payer, date, and notes.
* The amount must be greater than zero.
* The expense is linked to the logged-in user and selected group.
* The system calculates each person's share automatically.

---

### US4 — View Expense Summary

As a user, I want to view a summary of group expenses so that I know the total spending and each person's share.

Acceptance Criteria:

* The system shows the total expenses of the group.
* The system shows each expense with amount, payer, split count, and share.
* The summary only shows data belonging to the logged-in user.
* The summary updates after adding, editing, or deleting expenses.

---

### US5 — Edit and Delete Expense

As a user, I want to edit or delete an expense so that I can correct mistakes in my records.

Acceptance Criteria:

* The user can edit only their own expenses.
* The user can delete only their own expenses.
* After editing, the split calculation updates.
* After deleting, the expense disappears from the group summary.

---

## How to Run the Project

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git
cd YOUR_REPOSITORY_NAME
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

### 3. Activate the Virtual Environment

On Windows PowerShell:

```bash
.\venv\Scripts\Activate.ps1
```

If the environment uses `bin`:

```bash
.\venv\bin\Activate.ps1
```

### 4. Install Requirements

```bash
pip install -r requirements.txt
```

### 5. Initialize the Database

Run the application:

```bash
python app.py
```

Then open this link in the browser:

```text
http://127.0.0.1:5000/init-db
```

You should see:

```text
Database initialized successfully!
```

### 6. Start Using the Application

Open:

```text
http://127.0.0.1:5000/register
```

Create an account, login, and start using SplitMate.

---

## How to Run Tests

To run the unit tests:

```bash
pytest
```

Expected result:

```text
7 passed
```

---

## Demo Scenario

A simple demo flow:

1. Register a new user.
2. Login.
3. Create a group called `Home`.
4. Add two members, for example `Amr` and `Mohamed`.
5. Add an expense:

   * Title: Dinner
   * Amount: 300
   * Paid by: Amr
6. The system calculates each person's share as 150.
7. Edit the expense amount to 400.
8. The system updates each person's share to 200.
9. Delete the expense.
10. Logout.
11. Login with another user and confirm that the previous user's data is not visible.

---

## Notes

* The project uses raw SQL only.
* No ORM framework is used.
* User data is separated using `user_id`.
* The SQLite database file is ignored by Git.
* Unit tests focus on business logic, not routes.
* Git commits reference related user story IDs.
