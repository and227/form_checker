from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings


class Database:
    client: AsyncIOMotorClient = None


db = Database()


async def get_database() -> AsyncIOMotorClient:
    return db.client


async def connect_db():
    db.client = AsyncIOMotorClient(settings.MONGODB_URL)
    # db.client.form_database.form_collection.delete_many({})


async def disconnect_db():
    db.client.close()
