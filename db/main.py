from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, List
from .db_manager import DatabaseHandler

# =========================
# CONFIGURE DATABASE
# =========================
db = DatabaseHandler(
    host="localhost",
    database="your_db",
    user="your_user",
    password="your_password",
    port=5432
)
db.connect()

# =========================
# FASTAPI APP
# =========================
app = FastAPI(title="Postgres DB API")

# =========================
# REQUEST SCHEMAS
# =========================
class UserCreateRequest(BaseModel):
    email: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[str] = "scholar"

class UserAuthRequest(BaseModel):
    email: str
    password: str

class ProjectCreateRequest(BaseModel):
    name: str
    description: str
    created_by_user_id: str
    is_private: Optional[bool] = False

class ChatMessageRequest(BaseModel):
    session_id: str
    role: str
    content: str
    metadata: Optional[Dict] = None

# =========================
# USER ENDPOINTS
# =========================
@app.post("/users/create")
def create_user(request: UserCreateRequest):
    user_id = db.create_user(
        email=request.email,
        password=request.password,
        first_name=request.first_name,
        last_name=request.last_name,
        role=request.role
    )
    if not user_id:
        raise HTTPException(status_code=400, detail="User creation failed or email exists")
    return {"user_id": user_id}

@app.post("/users/authenticate")
def authenticate_user(request: UserAuthRequest):
    user = db.authenticate_user(email=request.email, password=request.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return user

@app.get("/users/{user_id}")
def get_user(user_id: str):
    user = db.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# =========================
# PROJECT ENDPOINTS
# =========================
@app.post("/projects/create")
def create_project(request: ProjectCreateRequest):
    project_id = db.create_project(
        name=request.name,
        description=request.description,
        created_by_user_id=request.created_by_user_id,
        is_private=request.is_private
    )
    if not project_id:
        raise HTTPException(status_code=400, detail="Project creation failed")
    return {"project_id": project_id}

@app.get("/users/{user_id}/projects")
def get_user_projects(user_id: str):
    return db.get_user_projects(user_id)

# =========================
# CHAT ENDPOINTS
# =========================
@app.post("/chat/messages/add")
def add_chat_message(request: ChatMessageRequest):
    message_id = db.add_chat_message(
        session_id=request.session_id,
        role=request.role,
        content=request.content,
        metadata=request.metadata
    )
    if not message_id:
        raise HTTPException(status_code=400, detail="Failed to add message")
    return {"message_id": message_id}

@app.get("/chat/{session_id}/messages")
def get_chat_messages(session_id: str, limit: int = 50):
    return db.get_chat_messages(session_id=session_id, limit=limit)

@app.get("/users/{user_id}/chat-sessions")
def get_user_chat_sessions(user_id: str, limit: int = 20):
    return db.get_user_chat_sessions(user_id=user_id, limit=limit)

# =========================
# AI MODELS
# =========================
@app.get("/models")
def get_models():
    return db.get_available_models()

# =========================
# HEALTH CHECK
# =========================
@app.get("/health")
def health_check():
    if db.test_connection():
        return {"status": "ok"}
    raise HTTPException(status_code=500, detail="Database connection failed")
