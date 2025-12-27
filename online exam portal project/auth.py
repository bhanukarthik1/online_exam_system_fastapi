from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database import get_db
from utils import hash_password, verify_password

router = APIRouter(prefix="/authorization", tags=["authorization"])

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    role: str


@router.post("/register")
def register(data: RegisterRequest):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (name,email,password,role) VALUES (%s,%s,%s,%s)",
            (data.name, data.email, hash_password(data.password), data.role)
        )
        db.commit()
        return {"message": "student added successfully"}

    except Exception as e:
        db.rollback()
        if "duplicate entry" in str(e).lower():
            raise HTTPException(status_code=400, detail="email already exists")
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        cursor.close()
        db.close()


@router.post("/login")
def login(email: str, password: str):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT * FROM users WHERE email=%s", (email,)
        )
        user = cursor.fetchone()

        if not user or not verify_password(password, user["password"]):
            raise HTTPException(status_code=401, detail="invalid credentials")

        return {
            "user_id": user["id"],
            "role": user["role"],
            "message": "login successful"
        }

    finally:
        cursor.close()
        db.close()
