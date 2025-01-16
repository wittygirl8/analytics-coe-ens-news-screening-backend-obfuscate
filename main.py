import os
from fastapi import FastAPI

# from .controllers import item_controller
from controllers import item_controller
from fastapi.middleware.cors import CORSMiddleware

docs_enabled = os.getenv("FASTAPI_ENV", "development") != "production"

app = FastAPI(
    docs_url="/docs",  # Ensure this is not set to None
    redoc_url="/redoc",  # Ensure this is not set to None
    swagger= 2.0
)
# Configure CORS middleware to allow requests from the React app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # React app's URL (or use "*" for all origins)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers (Content-Type, Authorization, etc.)
)
# Include the item routes
app.include_router(item_controller._rtr)
