# Import FastAPI, the framework for building APIs
from fastapi import FastAPI

# Import your chat-related routes (like endpoints for sending/receiving messages)
from routes.chat import router

# Import the function to initialize your database models
from models.postgres_model import init_models

# Create an instance of the FastAPI application
# This 'app' is what will run your server and handle requests
app = FastAPI()

# Include the chat router into the main app
# This allows the endpoints defined in routes/chat.py to be accessible
app.include_router(router)

# This function will run automatically when the FastAPI app starts
# It is used here to initialize your database tables and models
@app.on_event("startup")
async def on_startup():
    # Call the database initialization function
    await init_models()
