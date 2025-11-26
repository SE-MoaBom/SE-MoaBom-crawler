from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from utils import config
from .models import OTTModel, Base
from models.ott_enum import OTTPlatform
from sqlalchemy.future import select

engine = create_async_engine(
    config.DB_URL,
    echo=config.LOG_LEVEL == "DEBUG",
    pool_pre_ping=True,
    pool_recycle=3600,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    await engine.dispose()


async def seed_otts():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(OTTModel))
        existing_names = {o.name for o in result.scalars().all()}

        for ott in OTTPlatform:
            if ott.value not in existing_names:
                new_ott = OTTModel(
                    name=ott.value, price=ott.price, logo_url=ott.logo_url
                )
                session.add(new_ott)

        await session.commit()
