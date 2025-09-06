from fastapi import FastAPI
from routes.chat import router
from core.config import engine, Base

app = FastAPI()

# Include your chat router
app.include_router(router)

@app.on_event("startup")
async def on_startup():
    """
    Runs when the FastAPI app starts (development mode).
    Creates all tables automatically if they don't exist.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("✅ Database tables are ready!")
