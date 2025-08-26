from fastapi import FastAPI
from routes.chat import router


app = FastAPI()
# Include your chat router under a prefix, e.g. /api
app.include_router(router)




