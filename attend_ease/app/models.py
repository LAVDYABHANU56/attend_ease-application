from pydantic import BaseModel
from typing import Optional

# User Models
class UserRegister(BaseModel):
    name: str
    email: str
    password: str
    role: str  # "student" or "faculty"

class UserLogin(BaseModel):
    email: str
    password: str

# Session Models
class SessionCreate(BaseModel):
    subject: str
    room: str
    beacon_id: str  # UUID of the ESP32 beacon in this room
# Attendance Models
class AttendanceMark(BaseModel):
    session_id: str
    beacon_id: str
    gps_verified: bool
    ble_verified: bool
    face_verified: bool