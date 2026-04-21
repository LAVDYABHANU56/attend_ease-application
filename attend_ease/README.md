# AttendEase — Automated Attendance System

> **ME4131E Industrial IoT | Group 7 | Milestone 2**  
> Accurate, automated attendance through triple-layer verification: GPS · BLE Beacon · Face Recognition

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Project Structure](#project-structure)
4. [Prerequisites](#prerequisites)
5. [Setup & Installation](#setup--installation)
6. [Running the Project](#running-the-project)
7. [How to Use the App](#how-to-use-the-app)
8. [API Reference](#api-reference)
9. [Hardware Integration Guide](#hardware-integration-guide)
10. [Known Limitations (Prototype)](#known-limitations-prototype)
11. [Team](#team)

---

## Project Overview

AttendEase is a multi-layer IoT attendance system designed to eliminate proxy attendance and reduce the time wasted on manual roll calls. It verifies three things simultaneously before marking a student present:

| Layer | Technology | What it checks |
|-------|-----------|----------------|
| 1 | GPS Geofencing | Is the student on campus? |
| 2 | BLE Beacon (ESP32) | Is the student inside the correct classroom? |
| 3 | Face Recognition | Is this the correct person? |

All three must pass for attendance to be marked. The result is logged to a cloud dashboard with real-time analytics for faculty.

**Current State:** This is a working software prototype. GPS and BLE checks are simulated in the frontend. Face verification opens the device camera and confirms identity. The backend API and database are fully functional. Hardware integration points are clearly marked throughout the codebase.

---

## System Architecture

```
┌─────────────────────────────────────────────────────┐
│                    FRONTEND (HTML/JS)                │
│  index.html   →   student.html   →   verify.html    │
│  (Login)          (Sessions)        (3-layer check) │
│                                                      │
│  faculty.html  (Create/close sessions, view reports)│
└────────────────────┬────────────────────────────────┘
                     │ HTTP (localhost:8000)
┌────────────────────▼────────────────────────────────┐
│               BACKEND (FastAPI / Python)             │
│                                                      │
│  /auth       → Register, Login, JWT tokens          │
│  /sessions   → Create, list active, close sessions  │
│  /attendance → Mark attendance, view records        │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│                  DATABASE (MongoDB)                  │
│  users · sessions · attendance                      │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│              HARDWARE LAYER (ESP32) — Future        │
│  BLE Beacon broadcasting UUID per classroom         │
│  GPS coordinates validated server-side              │
│  Camera module for real face recognition            │
└─────────────────────────────────────────────────────┘
```

---

## Project Structure

```
attendease/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point, CORS config
│   ├── database.py          # MongoDB connection, collection references
│   ├── models.py            # Pydantic data models
│   └── routes/
│       ├── __init__.py
│       ├── auth.py          # /auth/register, /auth/login
│       ├── sessions.py      # /sessions/create, /sessions/active, /sessions/close
│       └── attendance.py    # /attendance/mark, /attendance/mystatus, /attendance/session
├── frontend/
│   ├── index.html           # Login / Register page
│   ├── student.html         # Student dashboard — view & join active sessions
│   ├── verify.html          # Triple-layer verification flow
│   └── faculty.html         # Faculty dashboard — create sessions, view attendance
├── .env                     # Environment variables (do not commit secrets)
├── .gitignore
└── README.md
```

---

## Prerequisites

Make sure the following are installed on your machine before setup:

| Tool | Version | Download |
|------|---------|----------|
| Python | 3.9 or higher | https://python.org |
| MongoDB Community | 6.x or higher | https://www.mongodb.com/try/download/community |
| Node.js (optional) | Any LTS | Only needed if you want `live-server` |
| Git | Any | https://git-scm.com |

---

## Setup & Installation

### Step 1 — Clone the repository

```bash
git clone https://github.com/your-org/attendease.git
cd attendease
```

### Step 2 — Create a Python virtual environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Mac / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` appear at the start of your terminal prompt.

### Step 3 — Install Python dependencies

```bash
pip install fastapi uvicorn motor passlib python-jose[cryptography] bcrypt python-dotenv
```

What each package does:
- `fastapi` — the web framework
- `uvicorn` — the server that runs FastAPI
- `motor` — async MongoDB driver
- `passlib` + `bcrypt` — password hashing
- `python-jose` — JWT token creation and verification
- `python-dotenv` — loads `.env` file variables

### Step 4 — Start MongoDB

**Windows** (MongoDB installed as a service — usually auto-starts):
```bash
net start MongoDB
```
If that fails, start it manually:
```bash
"C:\Program Files\MongoDB\Server\6.0\bin\mongod.exe" --dbpath="C:\data\db"
```

**Mac:**
```bash
brew services start mongodb-community
```

**Linux:**
```bash
sudo systemctl start mongod
```

Verify MongoDB is running by opening a new terminal and typing `mongosh`. You should get a MongoDB shell prompt. Type `exit` to leave.

### Step 5 — Configure environment variables

Open the `.env` file in the project root. It should contain:

```
MONGO_URL=mongodb://localhost:27017
DATABASE_NAME=attendease
SECRET_KEY=attendease_secret_key
```

You can change `SECRET_KEY` to any long random string for a production-style setup. For the prototype, the defaults work fine.

---

## Running the Project

You need **two things running at the same time**: the backend server and a way to serve the frontend.

### Terminal 1 — Start the Backend

From the project root with your virtual environment activated:

```bash
uvicorn app.main:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
```

Test it by opening `http://localhost:8000` in your browser. You should see:
```json
{"message": "AttendEase backend is running!"}
```

You can also explore all API endpoints at: `http://localhost:8000/docs`

### Terminal 2 — Serve the Frontend

**Option A — Using Python (simplest, no install needed):**
```bash
cd frontend
python -m http.server 3000
```

**Option B — Using Node live-server (auto-refreshes on save):**
```bash
npm install -g live-server
cd frontend
live-server --port=3000
```

Now open your browser and go to: **`http://localhost:3000`**

> ⚠️ Do NOT open the HTML files by double-clicking them. Always use the `http://localhost:3000` URL. Opening as `file://` causes localStorage and camera permissions to behave incorrectly.

---

## How to Use the App

### As a Faculty Member

1. Go to `http://localhost:3000` and register an account with role **Faculty**
2. Log in — you will be taken to the faculty dashboard
3. Enter a subject name and room number, then click **Start Session**
4. The session is now live and visible to all students
5. View real-time attendance as students mark themselves
6. Click **Close Session** when the class is over

### As a Student

1. Go to `http://localhost:3000` and register an account with role **Student**
2. Log in — you will be taken to the student dashboard
3. You will see all currently active sessions listed
4. Click **Mark Attendance** on the session for your class
5. The verification flow starts automatically:
   - **GPS check** — simulated (prototype), shows "On campus ✓"
   - **BLE check** — simulated (prototype), shows "Beacon found ✓"
   - **Face check** — opens your device camera, click **Verify Face**
6. After all three pass, attendance is marked and you are redirected back

---

## API Reference

All endpoints are available at `http://localhost:8000`. Full interactive docs at `http://localhost:8000/docs`.

### Auth

| Method | Endpoint | Body | Description |
|--------|----------|------|-------------|
| POST | `/auth/register` | `{name, email, password, role}` | Register a new user |
| POST | `/auth/login` | `{email, password}` | Login, returns JWT token |

### Sessions

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/sessions/create` | Faculty token | Create a new class session |
| GET | `/sessions/active` | None | List all active sessions |
| PUT | `/sessions/close/{session_id}` | Faculty token | Close a session |

### Attendance

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/attendance/mark` | Student token | Mark attendance with verification flags |
| GET | `/attendance/mystatus/{session_id}` | Student token | Check if already marked |
| GET | `/attendance/session/{session_id}` | Faculty token | Get all attendance for a session |

**Attendance mark body:**
```json
{
  "session_id": "string",
  "gps_verified": true,
  "ble_verified": true,
  "face_verified": true
}
```

---

## Hardware Integration Guide

This section is for team members integrating the ESP32 BLE beacons and real GPS/face verification into the prototype.

---

### BLE Beacon (ESP32) Integration

**What needs to happen:**  
Each classroom gets one ESP32 that continuously broadcasts a BLE advertisement with a unique UUID identifying that room. The student's phone scans for this beacon and if it's detected with sufficient signal strength (RSSI), the BLE check passes.

**Current state in code:**  
In `frontend/verify.html`, the BLE check is fully simulated:
```javascript
// Step 2 - BLE Check (mocked)
updateStep('bleStep', 'bleIcon', 'bleStatus', 'bleText', 'checking', 'Scanning for classroom beacon...');
await sleep(1500);
bleVerified = true;
updateStep('bleStep', 'bleIcon', 'bleStatus', 'bleText', 'verified', 'Beacon found ✓');
```

**To replace with real BLE scanning**, use the Web Bluetooth API:
```javascript
async function scanBLE() {
    try {
        const device = await navigator.bluetooth.requestDevice({
            filters: [{ name: 'AttendEase-Room402' }]  // match your ESP32 broadcast name
        });
        // Device found means student is in range
        bleVerified = true;
        updateStep('bleStep', 'bleIcon', 'bleStatus', 'bleText', 'verified', `Beacon found: ${device.name} ✓`);
    } catch (err) {
        updateStep('bleStep', 'bleIcon', 'bleStatus', 'bleText', 'failed', 'Not in classroom');
    }
}
```

**ESP32 Arduino code to broadcast BLE:**
```cpp
#include <BLEDevice.h>
#include <BLEAdvertising.h>

void setup() {
    BLEDevice::init("AttendEase-Room402");  // change per classroom
    BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
    pAdvertising->setScanResponse(true);
    pAdvertising->start();
}

void loop() {
    delay(1000);
}
```

Flash this to each ESP32 in each classroom. Change the device name to match the room (e.g. `AttendEase-Room101`, `AttendEase-Lab3`).

> ⚠️ Web Bluetooth only works in Chrome/Edge and requires HTTPS or localhost. It will not work in Firefox or Safari.

**Where to send beacon data to backend:**  
The `session_id` stored in the database corresponds to the room. You can add a `beacon_id` field to the sessions collection and validate server-side that the scanned beacon UUID matches the session's room.

In `app/models.py`, add:
```python
class SessionCreate(BaseModel):
    subject: str
    room: str
    beacon_id: str  # UUID of the ESP32 beacon in this room
```

In `app/routes/attendance.py`, validate:
```python
if data.beacon_id != session["beacon_id"]:
    raise HTTPException(status_code=400, detail="Wrong classroom beacon")
```

---

### GPS Geofencing Integration

**What needs to happen:**  
The student's phone checks its GPS coordinates. If the coordinates fall within a defined geofence (a radius around the campus), the GPS check passes.

**Current state in code:**  
In `frontend/verify.html`, the GPS check is fully simulated:
```javascript
// Step 1 - GPS Check (mocked)
updateStep('gpsStep', 'gpsIcon', 'gpsStatus', 'gpsText', 'checking', 'Checking location...');
await sleep(1500);
gpsVerified = true;
updateStep('gpsStep', 'gpsIcon', 'gpsStatus', 'gpsText', 'verified', 'On campus ✓');
```

**To replace with real GPS**, use the browser Geolocation API:
```javascript
async function checkGPS() {
    return new Promise((resolve, reject) => {
        navigator.geolocation.getCurrentPosition(position => {
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;

            // NIT Calicut campus center (replace with your campus coordinates)
            const CAMPUS_LAT = 11.3218;
            const CAMPUS_LON = 75.9345;
            const RADIUS_METERS = 500;

            const distance = getDistanceMeters(lat, lon, CAMPUS_LAT, CAMPUS_LON);

            if (distance <= RADIUS_METERS) {
                gpsVerified = true;
                updateStep('gpsStep', 'gpsIcon', 'gpsStatus', 'gpsText', 'verified', `On campus ✓ (${Math.round(distance)}m from center)`);
            } else {
                updateStep('gpsStep', 'gpsIcon', 'gpsStatus', 'gpsText', 'failed', 'Not on campus');
            }
            resolve();
        }, reject);
    });
}

function getDistanceMeters(lat1, lon1, lat2, lon2) {
    const R = 6371000;
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
              Math.cos(lat1 * Math.PI/180) * Math.cos(lat2 * Math.PI/180) *
              Math.sin(dLon/2) * Math.sin(dLon/2);
    return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
}
```

**To validate GPS server-side** (more secure, prevents spoofing):  
Send the raw coordinates to the backend and let the server calculate if they're within the geofence. Add lat/lon to the `AttendanceMark` model:
```python
class AttendanceMark(BaseModel):
    session_id: str
    gps_verified: bool
    ble_verified: bool
    face_verified: bool
    latitude: float   # add these
    longitude: float  # add these
```

---

### Face Recognition Integration

**What needs to happen:**  
The camera opens, captures the student's face, and compares it against the registered photo in the database.

**Current state in code:**  
The camera opens and after 1.5 seconds of "scanning", it marks face as verified for everyone. This is intentional for the prototype demo.

**To integrate real face recognition**, there are two approaches:

**Option A — Client-side using face-api.js (simpler):**
```html
<script src="https://cdn.jsdelivr.net/npm/face-api.js"></script>
```
```javascript
// Load models, then compare live camera frame against stored descriptor
await faceapi.nets.faceMatcher.loadFromUri('/models');
const detection = await faceapi.detectSingleFace(videoElement).withFaceLandmarks().withFaceDescriptor();
// Compare detection.descriptor against stored student descriptor
```

**Option B — Server-side using Python face_recognition library (more accurate):**

1. During registration, upload a photo of the student
2. Store the face encoding in MongoDB
3. During verification, capture a frame from the camera, send it to a new endpoint, and compare server-side

Add to `app/routes/attendance.py`:
```python
@router.post("/verify-face")
async def verify_face(file: UploadFile, credentials: ...):
    import face_recognition
    image = face_recognition.load_image_file(file.file)
    encoding = face_recognition.face_encodings(image)[0]
    
    user = decode_token(credentials.credentials)
    stored_encoding = await users_collection.find_one({"_id": user["id"]})["face_encoding"]
    
    match = face_recognition.compare_faces([stored_encoding], encoding)[0]
    return {"verified": bool(match)}
```

Install: `pip install face_recognition cmake dlib`

---

### ESP32 Full Wiring Reference

For the Wokwi simulation already built, the pin mapping is:

| Signal | ESP32 Pin | Notes |
|--------|-----------|-------|
| GPS input | GPIO 18 | HIGH = on campus |
| BLE input | GPIO 19 | HIGH = beacon detected |
| Face input | GPIO 21 | HIGH = face matched |
| Status LED | GPIO 22 | GREEN = all verified |
| Buzzer | GPIO 23 | Beeps on success |

In production, these would be replaced by actual sensor readings rather than manual pin inputs.

---

## Known Limitations (Prototype)

| Feature | Current State | Production Fix |
|---------|--------------|----------------|
| GPS check | Simulated in frontend | Browser Geolocation API + server-side geofence |
| BLE check | Simulated in frontend | Web Bluetooth API + ESP32 beacons |
| Face recognition | Camera opens, auto-verifies | face-api.js or server-side face_recognition |
| HTTPS | Localhost only | Deploy with SSL cert for camera/BLE to work on mobile |
| Secret key | Hardcoded in source | Move to .env, never commit |
| Face photo storage | Not implemented | Add file upload at registration |

---

## Team

**Group 7 — ME4131E Industrial IoT**

Aadarsh P B · Ashlin M L · Atheena K J · Bhadrra R · Karthik Santhosh · L. Bhanuchander · Lokesh · Manjunadha L · Mogesh · Navneeth Shajil

---

*AttendEase — Attendance. Made Effortless.*
