from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import DATABASE_URL, SYNC_DATABASE_URL
from app.models import Base


# This is the connection pool for FastAPI route handlers
async_engine = create_async_engine(DATABASE_URL)

# Creating a session/ connection
AsyncSessionLocal = async_sessionmaker(async_engine, expire_on_commit=False)

# This engine is for the subscriber threads (notification, analytics and ...)
sync_engine = create_engine(SYNC_DATABASE_URL)
SyncSessionLocal = sessionmaker(sync_engine)

# Startup function - to create tables if doesnot exists

async def create_tables():
  async with async_engine.begin() as conn:
    await conn.run_sync(Base.metadata.create_all)