from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from sqlalchemy import select, insert
from werkzeug.security import generate_password_hash, check_password_hash

# Import database models and engine from db.py
from db import engine, users_table, todos_table

app = Flask(__name__)
app.secret_key = "replace-this-with-a-secure-random-secret-key"

# Live reloading & static file cache configuration
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


# -------------------------------------------------------------
# 1. AUTHENTICATION ROUTES
# -------------------------------------------------------------

# GET /register - Render HTML Page
@app.route("/register", methods=["GET"])
def show_register_page():
    return render_template("register.html")


# POST /auth/register & POST /register - Handle User Registration
@app.route("/auth/register", methods=["POST"])
@app.route("/register", methods=["POST"])
def handle_register():
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

    if not request.is_json:
        return redirect(url_for("show_login_page"))

    return jsonify({
        "message": "User registered successfully",
        "user_id": new_user_id
    }), 201


# GET /login - Render HTML Page
@app.route("/login", methods=["GET"])
def show_login_page():
    return render_template("login.html")


# POST /auth/login & POST /login - Handle User Authentication
@app.route("/auth/login", methods=["POST"])
@app.route("/login", methods=["POST"])
def handle_login():
    data = request.get_json() if request.is_json else request.form
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    with engine.connect() as conn:
        stmt = select(users_table).where(users_table.c.email == email)
        user = conn.execute(stmt).fetchone()

        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            session["user_name"] = user.name

            if request.is_json:
                return jsonify({"message": "Login successful", "user_id": user.id, "name": user.name}), 200

            return redirect(url_for("todo_list"))

    if request.is_json:
        return jsonify({"error": "Invalid email or password"}), 401

    return render_template("login.html", error="Invalid email or password.")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("show_login_page"))


# -------------------------------------------------------------
# 2. FRONTEND HTML ROUTING
# -------------------------------------------------------------

@app.route("/")
@app.route("/todos", methods=["GET"])
def todo_list():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("show_login_page"))
    return render_template("todo_list.html")


@app.route("/todos/<int:todo_id>", methods=["GET"])
def todo_details(todo_id):
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("show_login_page"))
    return render_template("todo_details.html")


# -------------------------------------------------------------
# 3. JSON API ROUTES FOR JAVASCRIPT
# -------------------------------------------------------------

# GET /api/me - Return Current User Info
@app.route("/api/me", methods=["GET"])
def get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify({
        "id": user_id,
        "name": session.get("user_name", "User")
    }), 200


# GET /api/todos - Hierarchical JSON list of parent and child todos
@app.route("/api/todos", methods=["GET"])
def get_hierarchical_todos():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    with engine.connect() as conn:
        stmt = select(todos_table).where(todos_table.c.user_id == user_id)
        all_todos = conn.execute(stmt).fetchall()

    todo_dict = {}
    parent_todos = []

    for row in all_todos:
        item = {
            "id": row.id,
            "title": row.title,
            "description": row.description,
            "parent_todo_id": row.parent_todo_id,
            "subtodos": []
        }
        todo_dict[row.id] = item

    for item in todo_dict.values():
        parent_id = item["parent_todo_id"]
        if parent_id is None:
            parent_todos.append(item)
        elif parent_id in todo_dict:
            todo_dict[parent_id]["subtodos"].append(item)

    return jsonify(parent_todos), 200


# POST /api/todos - Create new parent or child task
@app.route("/api/todos", methods=["POST"])
def create_todo():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json() or {}
    title = data.get("title")

    if not title:
        return jsonify({"error": "Title is required"}), 400

    parent_todo_id = data.get("parent_todo_id")
    if parent_todo_id is not None:
        try:
            parent_todo_id = int(parent_todo_id)
        except ValueError:
            parent_todo_id = None

    with engine.connect() as conn:
        stmt = insert(todos_table).values(
            user_id=user_id,
            title=title,
            description=data.get("description"),
            parent_todo_id=parent_todo_id
        )
        result = conn.execute(stmt)
        conn.commit()
        new_id = result.inserted_primary_key[0]

    return jsonify({
        "message": "Todo created successfully",
        "id": new_id,
        "title": title
    }), 201


if __name__ == "__main__":
    app.run(debug=True)