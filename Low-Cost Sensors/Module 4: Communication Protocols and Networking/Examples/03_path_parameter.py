"""
Simple Server that takes path parameters
"""

# Use FastAPI as the HTTP server implementation
from fastapi import FastAPI

# Instantiate the server
app = FastAPI()

# Give the request two path parameters
@app.get("/parameters/{name}/{value}")
async def parameters(name: str, value: float):
    return f"Hello to the path parameters {name} with {value}."
