from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from sqlalchemy import select
from werkzeug.security import generate_password_hash, check_password_hash

# Import database models and engine from db.py
from db import engine, users_table, todos_table

app = Flask(__name__)
app.secret_key = "replace-this-with-a-secure-random-secret-key"

# --- Web Route Renderers ---
@app.route("/login")
def login_page():
    return render_template("login.html")

@app.route("/register")
def register_page():
    return render_template("register.html")

# --- Authentication API Routes ---

@app.route("/auth/register", methods=["POST"])
def register():
    data = request.get_json() if request.is_json else request.form
    email = data.get("email")
    password = data.get("password")
    name = data.get("name")

    if not email or not password or not name:
        return jsonify({"error": "Missing required fields"}), 400

    hashed_password = generate_password_hash(password)

    with engine.connect() as conn:
        stmt_check = select(users_table).where(users_table.c.email == email)
        existing_user = conn.execute(stmt_check).fetchone()
        if existing_user:
            return jsonify({"error": "Email is already registered"}), 409

        stmt_insert = users_table.insert().values(
            email=email,
            password=hashed_password,
            name=name
        )
        result = conn.execute(stmt_insert)
        conn.commit()
        new_user_id = result.inserted_primary_key[0]

    return jsonify({
        "message": "User registered successfully",
        "user_id": new_user_id
    }), 201


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        with engine.connect() as conn:
            user = conn.execute(
                select(users_table).where(users_table.c.email == email)
            ).fetchone()

            # Check if user exists and password is correct
            if user and check_password_hash(user.password, password):
                session["user_id"] = user.id
                session["user_name"] = user.name
                
                # CRITICAL: Redirect to /todos on successful login
                return redirect(url_for("todo_list"))

            # If login fails, reload login page with message
            flash("Invalid email or password.", "error")
            return redirect(url_for("login"))

    return render_template("login.html")


if __name__ == "__main__":
    app.run(debug=True)