from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.database import attendance_collection, sessions_collection
from app.models import AttendanceMark
from jose import jwt
from datetime import datetime
from bson import ObjectId

router = APIRouter()

SECRET_KEY = "attendease_secret_key"
ALGORITHM = "HS256"
security = HTTPBearer()

def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/mark")
async def mark_attendance(data: AttendanceMark, credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    user = decode_token(token)

    # Check if session exists and is active
    session = await sessions_collection.find_one({
        "_id": ObjectId(data.session_id),
        "active": True
    })
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or inactive")
    if data.beacon_id != session["beacon_id"]:
        raise HTTPException(status_code=400, detail="Wrong classroom beacon")
    
    # Check if already marked
    existing = await attendance_collection.find_one({
        "student_id": user["id"],
        "session_id": data.session_id
    })
    if existing:
        raise HTTPException(status_code=400, detail="Attendance already marked")

    # Check all three verifications
    if not (data.gps_verified and data.ble_verified and data.face_verified):
        raise HTTPException(status_code=400, detail="Verification failed")

    # Mark attendance
    record = {
        "student_id": user["id"],
        "student_name": user["name"],
        "session_id": data.session_id,
        "subject": session["subject"],
        "room": session["room"],
        "gps_verified": data.gps_verified,
        "ble_verified": data.ble_verified,
        "face_verified": data.face_verified,
        "timestamp": datetime.utcnow()
    }
    await attendance_collection.insert_one(record)
    return {"message": "Attendance marked successfully"}

@router.get("/session/{session_id}")
async def get_session_attendance(session_id: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    user = decode_token(token)

    if user["role"] != "faculty":
        raise HTTPException(status_code=403, detail="Only faculty can view attendance")

    records = []
    async for record in attendance_collection.find({"session_id": session_id}):
        records.append({
            "student_name": record["student_name"],
            "timestamp": str(record["timestamp"]),
            "gps_verified": record["gps_verified"],
            "ble_verified": record["ble_verified"],
            "face_verified": record["face_verified"]
        })
    return records

@router.get("/mystatus/{session_id}")
async def my_attendance_status(session_id: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    user = decode_token(token)

    record = await attendance_collection.find_one({
        "student_id": user["id"],
        "session_id": session_id
    })
    if record:
        return {"present": True, "timestamp": str(record["timestamp"])}
    return {"present": False}