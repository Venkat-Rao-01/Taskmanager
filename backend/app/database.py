from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.config import get_settings


settings = get_settings()
client = AsyncIOMotorClient(settings.mongodb_uri)
db: AsyncIOMotorDatabase = client[settings.database_name]


async def ensure_indexes() -> None:
    await db.users.create_index("email", unique=True)
    await db.projects.create_index("members")
    await db.tasks.create_index([("project_id", 1), ("assignee_id", 1), ("status", 1)])
    await db.tasks.create_index("due_date")
