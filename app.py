# app.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from db.db_handling import DatabaseHandler
from dotenv import load_dotenv
import os

# =========================
# LOAD ENV VARIABLES
# =========================
load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST', '127.0.0.1'),
    'database': os.getenv('DB_NAME', 'chatting'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'placeholder'),
    'port': int(os.getenv('DB_PORT', 5432))
}

db = DatabaseHandler(**DB_CONFIG)
db.connect()

app = FastAPI(title="Chatting API")

# =========================
# SCHEMAS
# =========================
class UserCreate(BaseModel):
    email: str
    password: str
    first_name: str = None
    last_name: str = None
    role: str = "scholar"

class UserLogin(BaseModel):
    email: str
    password: str

# =========================
# ROUTES
# =========================

@app.get("/")
def home():
    return {"message": "✅ FastAPI server is running!"}

@app.post("/register")
def register(user: UserCreate):
    user_id = db.create_user(
        email=user.email,
        password=user.password,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role
    )
    if not user_id:
        raise HTTPException(status_code=400, detail="User creation failed")
    return {"success": True, "user_id": user_id}

@app.post("/login")
def login(user: UserLogin):
    user_info = db.authenticate_user(
        email=user.email,
        password=user.password
    )
    if not user_info:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"success": True, "user": user_info}

@app.get("/projects/{user_id}")
def get_projects(user_id: str):
    projects = db.get_user_projects(user_id)
    return {"projects": projects}

@app.get("/chats/{user_id}")
def get_chats(user_id: str):
    chats = db.get_user_chat_sessions(user_id)
    return {"chat_sessions": chats}

@app.get("/models")
def get_models():
    models = db.get_available_models()
    return {"models": models}

# =========================
# RUN SERVER
# =========================
# uvicorn app:app --reload
