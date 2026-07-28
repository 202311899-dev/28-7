from datetime import datetime
from sqlalchemy import (
    create_engine, MetaData, Table, Column, 
    Integer, String, Text, Boolean, DateTime, ForeignKey
)

# Engine setup (using SQLite for local development)
# Replace with your local Postgres username, password, host, port, and db name
# Replace with your local Postgres username, password, host, port, and db name
DATABASE_URL = "postgresql://postgres:omar123@localhost:5432/todo_db"
engine = create_engine(DATABASE_URL, echo=True)

# Metadata object holding schema definitions
metadata = MetaData()

# 1. Users Table
users_table = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("email", String(255), nullable=False, unique=True),
    Column("password", String(255), nullable=False),
    Column("name", String(255), nullable=False),
    Column("created_at", DateTime, default=datetime.utcnow)
)

# 2. Todos Table (Self-referencing foreign key for subtasks)
todos_table = Table(
    "todos",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    Column("title", String(255), nullable=False),
    Column("description", Text, nullable=True),
    Column("parent_todo_id", Integer, ForeignKey("todos.id", ondelete="CASCADE"), nullable=True),
    Column("created_at", DateTime, default=datetime.utcnow),
    Column("completed", Boolean, default=False)
)