from fastapi import FastAPI
from routes.chat import router
from models.postgres_model import init_models

app = FastAPI()

# Include your chat router
app.include_router(router)
@app.on_event("startup")
async def on_startup():
    await init_models()