from collections.abc import AsyncGenerator
from app.core.config import settings
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

DATABASE_URL = settings.DATABASE_URL_ASYNC

async_engine = create_async_engine(DATABASE_URL, future=True, echo=False, pool_pre_ping=True)

async_session_factory = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session