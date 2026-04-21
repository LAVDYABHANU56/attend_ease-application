from fastapi import APIRouter, HTTPException
from app.database import sessions_collection
from app.models import SessionCreate
from datetime import datetime
from bson import ObjectId

router = APIRouter()

# ✅ CREATE SESSION (NO AUTH FOR NOW)
@router.post("/create")
async def create_session(session: SessionCreate):

    new_session = {
        "subject": session.subject,
        "room": session.room,
        "beacon_id": session.beacon_id,   # 🔥 IMPORTANT FIX
        "faculty_name": "Demo Faculty",   # temporary
        "active": True,
        "created_at": datetime.utcnow()
    }

    result = await sessions_collection.insert_one(new_session)

    return {
        "message": "Session created",
        "session_id": str(result.inserted_id)
    }


# ✅ GET ACTIVE SESSIONS
@router.get("/active")
async def get_active_sessions():
    sessions = []
    async for session in sessions_collection.find({"active": True}):
        sessions.append({
            "session_id": str(session["_id"]),
            "subject": session["subject"],
            "room": session["room"],
            "beacon_id": session["beacon_id"],
            "faculty_name": session["faculty_name"],
            "created_at": str(session["created_at"])
        })
    return sessions


# ✅ CLOSE SESSION
@router.put("/close/{session_id}")
async def close_session(session_id: str):

    await sessions_collection.update_one(
        {"_id": ObjectId(session_id)},
        {"$set": {"active": False}}
    )

    return {"message": "Session closed"}