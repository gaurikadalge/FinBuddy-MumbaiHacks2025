# backend/core/database.py

from typing import Optional, Any
from motor.motor_asyncio import AsyncIOMotorClient
from motor.core import AgnosticClient
from backend.core.config import settings


class MongoConnection:
    """
    Clean and production-ready MongoDB connection manager.
    Handles async init, pooling, and safe shutdown.
    """

    def __init__(self):
        self.client: Optional[AgnosticClient] = None
        self.database: Optional[Any] = None

    async def connect(self):
        """
        Create async MongoDB client and test connection.
        """
        try:
            self.client = AsyncIOMotorClient(
                settings.MONGO_URI,
                maxPoolSize=20,
                minPoolSize=2,
                serverSelectionTimeoutMS=5000,
            )

            # Select DB
            self.database = self.client[settings.MONGO_DB_NAME]

            # Test ping
            await self.client.admin.command("ping")
            print(f"✅ MongoDB Connected → {settings.MONGO_DB_NAME}")

        except Exception as e:
            print(f"❌ MongoDB Connection Failed: {e}")
            # Make sure we reset state on failure
            self.client = None
            self.database = None
            raise RuntimeError("Cannot connect to MongoDB. Check your MONGO_URI.") from e

    async def disconnect(self):
        """
        Close the connection safely.
        """
        if self.client is not None:
            self.client.close()
            self.client = None
            self.database = None
            print("❌ MongoDB Disconnected")

    def get_db(self):
        """
        Return DB instance if available.
        """
        # IMPORTANT: compare with None, don't use truthiness
        if self.database is None:
            raise RuntimeError("MongoDB is not connected yet.")
        return self.database

    def get_collection(self, name: str):
        """
        Get a MongoDB collection by name.
        """
        # IMPORTANT: compare with None, don't use truthiness
        if self.database is None:
            raise RuntimeError("MongoDB is not connected yet.")
        return self.database[name]


# --------------------------
# Global instance
# --------------------------

mongo = MongoConnection()


# --------------------------
# Lifespan Hooks
# --------------------------

async def connect_to_mongo():
    await mongo.connect()


async def close_mongo_connection():
    await mongo.disconnect()


# --------------------------
# Collection Access Functions
# --------------------------

def get_transactions_collection():
    """
    Direct function to get transactions collection.
    """
    return mongo.get_collection("transactions")
