from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB connection details
# Option 1: Use full connection string (recommended)
MONGO_URI = os.getenv("MONGO_URI")

# Option 2: Build connection string from components
if not MONGO_URI:
    MONGO_USERNAME = os.getenv("MONGO_USERNAME", "drtoolofficial_db_user")
    MONGO_PASSWORD = os.getenv("MONGO_PASSWORD", "alwVEEBPJLVp7TAa")
    MONGO_HOST = os.getenv("MONGO_HOST", "localhost:27017")  # Default to localhost
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "drtoolofficial_db")
    USE_SRV = os.getenv("MONGO_USE_SRV", "false").lower() == "true"
    
    # Construct MongoDB URI
    if USE_SRV:
        # MongoDB Atlas SRV connection
        MONGO_URI = f"mongodb+srv://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_HOST}/{MONGO_DB_NAME}?retryWrites=true&w=majority"
    else:
        # Standard MongoDB connection
        MONGO_URI = f"mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_HOST}/{MONGO_DB_NAME}?retryWrites=true&w=majority"

MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "drtoolofficial_db")

# Global MongoDB client
client: AsyncIOMotorClient = None
database = None


async def connect_to_mongo():
    """Create database connection"""
    global client, database
    try:
        print(f"🔌 Attempting to connect to MongoDB...")
        print(f"📍 Connection URI: {MONGO_URI.split('@')[0]}@***")  # Hide password in logs
        
        client = AsyncIOMotorClient(
            MONGO_URI,
            serverSelectionTimeoutMS=10000  # Increased timeout
        )
        # Test the connection
        await client.admin.command('ping')
        database = client[MONGO_DB_NAME]
        print(f"✅ Connected to MongoDB: {MONGO_DB_NAME}")
        return database
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        print(f"💡 Tip: Check your MONGO_URI or connection details in .env file")
        raise


async def close_mongo_connection():
    """Close database connection"""
    global client
    if client:
        client.close()
        print("✅ MongoDB connection closed")


def get_database():
    """Get database instance"""
    return database

