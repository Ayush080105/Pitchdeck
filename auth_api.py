import os
from fastapi import FastAPI, HTTPException, Depends, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
import sqlite3
from datetime import datetime, timedelta

SECRET_KEY = os.getenv("AUTH_SECRET_KEY", "supersecretkey")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

app = FastAPI()

# --- SQLite Setup ---
DB_PATH = "users.db"
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def create_user_table():
    conn = get_db()
    conn.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        hashed_password TEXT NOT NULL
    )
    """)
    conn.commit()
    conn.close()
create_user_table()

# --- Models ---
class User(BaseModel):
    username: str
    email: str

class UserInDB(User):
    hashed_password: str

# --- Utility Functions ---
def get_user_by_username(username: str) -> Optional[UserInDB]:
    conn = get_db()
    cur = conn.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()
    if row:
        return UserInDB(username=row["username"], email=row["email"], hashed_password=row["hashed_password"])
    return None

def get_user_by_email(email: str) -> Optional[UserInDB]:
    conn = get_db()
    cur = conn.execute("SELECT * FROM users WHERE email = ?", (email,))
    row = cur.fetchone()
    conn.close()
    if row:
        return UserInDB(username=row["username"], email=row["email"], hashed_password=row["hashed_password"])
    return None

def create_user(username: str, email: str, password: str):
    hashed_password = pwd_context.hash(password)
    conn = get_db()
    try:
        conn.execute("INSERT INTO users (username, email, hashed_password) VALUES (?, ?, ?)", (username, email, hashed_password))
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Username or email already registered.")
    finally:
        conn.close()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(username: str, password: str):
    user = get_user_by_username(username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# --- API Endpoints ---
@app.post("/signup")
def signup(username: str = Form(...), email: str = Form(...), password: str = Form(...)):
    if get_user_by_username(username) or get_user_by_email(email):
        raise HTTPException(status_code=400, detail="Username or email already registered.")
    create_user(username, email, password)
    return {"msg": "Signup successful"}

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/me")
def read_users_me(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = get_user_by_username(username)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {"username": user.username, "email": user.email} 