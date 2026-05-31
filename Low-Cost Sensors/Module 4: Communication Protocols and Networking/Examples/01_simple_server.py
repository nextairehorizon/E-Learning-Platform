"""
Simple Server with one get method
"""

# Use FastAPI as the HTTP server implementation
from fastapi import FastAPI

# Instantiate the server
app = FastAPI()

# Give the server one endpoint
@app.get("/hello")
async def hello():
    return "Hello from the server"

