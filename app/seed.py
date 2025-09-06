import asyncio
from models.postgres_model import User, Message  # import your SQLAlchemy models
from core.config import async_session, engine, Base

async def seed_data():
    # Ensure tables exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        async with session.begin():
            # Add sample users
            user1 = User(name="Mark", email="mark@example.com")
            user2 = User(name="Alice", email="alice@example.com")
            session.add_all([user1, user2])

        await session.commit()

    async with async_session() as session:
        async with session.begin():
            # Add sample messages
            msg1 = Message(user_id=1, content="Hello World!")
            msg2 = Message(user_id=2, content="Hi Mark!")
            session.add_all([msg1, msg2])

        await session.commit()

    print("Database seeded successfully!")

if __name__ == "__main__":
    asyncio.run(seed_data())
