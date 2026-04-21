from motor.motor_asyncio import AsyncIOMotorClient

# MongoDB connection
MONGO_URL = "mongodb://127.0.0.1:27017"
DATABASE_NAME = "attendease"

client = AsyncIOMotorClient(MONGO_URL)

# Test connection (important)
try:
    print("Connected to MongoDB")
except Exception as e:
    print("MongoDB connection error:", e)

# Database
db = client[DATABASE_NAME]

# Collections
users_collection = db["users"]
sessions_collection = db["sessions"]
attendance_collection = db["attendance"]