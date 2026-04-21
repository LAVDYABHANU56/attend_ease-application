from fastapi import APIRouter, HTTPException
from app.database import users_collection
from app.models import UserRegister, UserLogin
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta

router = APIRouter()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = "attendease_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 day


# ✅ FIXED HASH FUNCTION (bcrypt safe)
def hash_password(password: str):
    password = password[:72]  # 🔥 IMPORTANT FIX
    return pwd_context.hash(password)


# ✅ FIXED VERIFY FUNCTION
def verify_password(plain, hashed):
    return pwd_context.verify(plain[:72], hashed)


def create_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ✅ REGISTER
@router.post("/register")
async def register(user: UserRegister):
    existing = await users_collection.find_one({"email": user.email})

    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = hash_password(user.password)

    new_user = {
        "name": user.name,
        "email": user.email,
        "password": hashed_password,
        "role": user.role
    }

    await users_collection.insert_one(new_user)

    return {"message": "User registered successfully"}


# ✅ LOGIN
@router.post("/login")
async def login(user: UserLogin):
    db_user = await users_collection.find_one({"email": user.email})

    if not db_user:
        raise HTTPException(status_code=400, detail="User not found")

    if not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=400, detail="Incorrect password")

    token = create_token({
        "id": str(db_user["_id"]),
        "email": db_user["email"],
        "role": db_user["role"],
        "name": db_user["name"]
    })

    return {
        "token": token,
        "role": db_user["role"],
        "name": db_user["name"]
    }