from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routes import auth, sessions, attendance

app = FastAPI(title="AttendEase API")

# ✅ 1. CORS (keep early)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ 2. REGISTER ROUTES FIRST (VERY IMPORTANT)
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(sessions.router, prefix="/sessions", tags=["Sessions"])
app.include_router(attendance.router, prefix="/attendance", tags=["Attendance"])

# ✅ 3. STATIC FILES LAST (ONLY ONCE)
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

# Optional root check
@app.get("/api")
def read_root():
    return {"message": "AttendEase backend is running!"}